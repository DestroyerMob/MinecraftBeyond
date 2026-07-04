#!/usr/bin/env python3
"""Cross-platform maintenance tools for the Minecraft Beyond pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
PACK_DIR = REPO_ROOT / "pack"
PACK_MODS_DIR = PACK_DIR / "mods"
PACK_SHADERPACKS_DIR = PACK_DIR / "shaderpacks"
PACK_TOML = PACK_DIR / "pack.toml"
INDEX_TOML = PACK_DIR / "index.toml"
LOCAL_MODS_JSON = TOOLS_DIR / "local-mods.json"
DEV_ENV_LOCAL = TOOLS_DIR / "dev-env.local.json"
DEFAULT_SOURCE_ROOT = Path.home() / "Documents" / "minecraft-mod-sources"
DEFAULT_PRISM_MINECRAFT_DIR = REPO_ROOT / "minecraft"
DEFAULT_PRISM_MODS_DIR = DEFAULT_PRISM_MINECRAFT_DIR / "mods"
DEFAULT_PRISM_SHADERPACKS_DIR = DEFAULT_PRISM_MINECRAFT_DIR / "shaderpacks"
PACKWIZ_INSTALLER_BOOTSTRAP_URL = (
    "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/"
    "packwiz-installer-bootstrap.jar"
)
PACKWIZ_INSTALLER_BOOTSTRAP = TOOLS_DIR / "bin" / "packwiz-installer-bootstrap.jar"
PACKWIZ_INSTALLER_MAIN = TOOLS_DIR / "bin" / "packwiz-installer.jar"
PACK_LOCAL_QUALITY_APPLIER = TOOLS_DIR / "modqualitypicker_prism.py"
PYTHON_COMPAT_DIR = TOOLS_DIR / "python_compat"


class ToolError(RuntimeError):
    pass


@dataclass
class Check:
    name: str
    status: str
    detail: str = ""
    required: bool = False

    @property
    def ok(self) -> bool:
        return self.status in {"ok", "found", "clean", "matched"}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ToolError(f"Invalid JSON in {path}: {exc}") from exc


def load_dev_env() -> dict:
    return load_json(DEV_ENV_LOCAL)


def expand_path(value: str | os.PathLike[str] | None, base: Path = REPO_ROOT) -> Path | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    expanded = os.path.expandvars(os.path.expanduser(text))
    path = Path(expanded)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def setting(
    cli_value: str | None,
    env_names: Sequence[str],
    dev_env: dict,
    dev_key: str,
    default: Path | str | None,
) -> Path | None:
    if cli_value:
        return expand_path(cli_value)

    for env_name in env_names:
        value = os.environ.get(env_name)
        if value:
            return expand_path(value)

    value = dev_env.get(dev_key)
    if value:
        return expand_path(value)

    if default is None:
        return None
    return expand_path(default)


def run(
    command: Sequence[str | os.PathLike[str]],
    *,
    cwd: Path = REPO_ROOT,
    dry_run: bool = False,
    capture: bool = False,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [str(part) for part in command]
    if dry_run:
        print(f"DRY RUN: ({cwd}) {' '.join(cmd)}")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    try:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            env=env,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ToolError(f"Command not found: {cmd[0]}") from exc

    if check and completed.returncode != 0:
        message = f"{' '.join(cmd)} failed with exit code {completed.returncode}"
        if capture:
            details = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
            if details:
                message = f"{message}\n{details.strip()}"
        raise ToolError(message)

    return completed


def download_file(url: str, destination: Path, *, dry_run: bool = False) -> None:
    if dry_run:
        print(f"DRY RUN: download {url} -> {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            with temporary.open("wb") as handle:
                shutil.copyfileobj(response, handle)
        temporary.replace(destination)
    except Exception as exc:
        if temporary.exists():
            temporary.unlink()
        raise ToolError(f"Failed to download {url}: {exc}") from exc


def find_free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_http(url: str, process: subprocess.Popen[bytes], timeout_seconds: float = 15.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise ToolError(f"packwiz serve exited early with code {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return
        except Exception as exc:
            last_error = exc
        time.sleep(0.25)

    detail = f": {last_error}" if last_error else ""
    raise ToolError(f"Timed out waiting for packwiz serve at {url}{detail}")


def command_output(command: Sequence[str], cwd: Path = REPO_ROOT) -> str:
    completed = run(command, cwd=cwd, capture=True)
    return completed.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_line_match(path: Path, pattern: str) -> str | None:
    regex = re.compile(pattern)
    for line in path.read_text(encoding="utf-8").splitlines():
        match = regex.search(line)
        if match:
            return match.group(1)
    return None


def packwiz_metadata_filename(path: Path) -> str | None:
    return first_line_match(path, r"filename\s*=\s*['\"]([^'\"]+)['\"]")


def normalize_shader_metadata(text: str) -> str:
    normalized: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if re.fullmatch(r"side\s*=\s*['\"]\s*['\"]", line):
            normalized.append("side = 'client'")
            continue
        if re.fullmatch(r"url\s*=\s*['\"]\s*['\"]", line):
            continue
        normalized.append(raw_line)
    return "\n".join(normalized) + "\n"


def parse_pack_index_hash() -> str | None:
    if not PACK_TOML.exists():
        return None

    in_index = False
    for raw_line in PACK_TOML.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[index]":
            in_index = True
            continue
        if line.startswith("[") and line != "[index]":
            in_index = False
        if in_index:
            match = re.match(r'hash\s*=\s*"([^"]+)"', line)
            if match:
                return match.group(1)
    return None


def parse_index_files() -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    if not INDEX_TOML.exists():
        return files

    for raw_line in INDEX_TOML.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[[files]]":
            if current:
                files.append(current)
            current = {}
            continue
        if current is None:
            continue
        match = re.match(r'([A-Za-z0-9_-]+)\s*=\s*"([^"]*)"', line)
        if match:
            current[match.group(1)] = match.group(2)
    if current:
        files.append(current)
    return files


def read_local_mods(path: Path = LOCAL_MODS_JSON, *, include_disabled: bool = False) -> list[dict]:
    data = load_json(path)
    mods = data.get("mods", [])
    if not isinstance(mods, list):
        raise ToolError(f"Expected a mods array in {path}")
    if include_disabled:
        return mods
    return [mod for mod in mods if mod.get("enabled", True)]


def resolve_packwiz(dev_env: dict, explicit: str | None = None) -> Path | None:
    explicit_path = setting(
        explicit,
        ("MINECRAFT_BEYOND_PACKWIZ", "PACKWIZ"),
        dev_env,
        "packwiz",
        None,
    )
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(explicit_path)

    bin_dir = TOOLS_DIR / "bin"
    candidates.extend(
        [
            bin_dir / "packwiz.exe",
            bin_dir / "packwiz",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    found = shutil.which("packwiz")
    return Path(found).resolve() if found else None


def resolve_java(dev_env: dict, explicit_home: str | None = None) -> Path | None:
    java_home = setting(
        explicit_home,
        ("MINECRAFT_BEYOND_JAVA_HOME", "JAVA_HOME"),
        dev_env,
        "javaHome",
        None,
    )
    candidates: list[Path] = []
    if java_home:
        candidates.append(java_home / "bin" / ("java.exe" if os.name == "nt" else "java"))

    found = shutil.which("java")
    if found:
        candidates.append(Path(found))

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def resolve_quality_applier(dev_env: dict) -> Path | None:
    candidates = [PACK_LOCAL_QUALITY_APPLIER]
    source_root = setting(
        None,
        ("MINECRAFT_MOD_SOURCE_ROOT",),
        dev_env,
        "sourceRoot",
        DEFAULT_SOURCE_ROOT,
    )
    if source_root:
        candidates.append(source_root / "ModQualityPicker" / "tools" / "modqualitypicker_prism.py")

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def python_compat_environment() -> dict[str, str] | None:
    if sys.version_info >= (3, 11) or not PYTHON_COMPAT_DIR.exists():
        return None

    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    paths = [str(PYTHON_COMPAT_DIR)]
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def quality_pending_profile_path(minecraft_dir: Path) -> Path:
    return minecraft_dir / "config" / "modqualitypicker" / "pending-profile.json"


def apply_quality_profile_after_sync(dev_env: dict, minecraft_dir: Path, *, dry_run: bool, skip: bool) -> None:
    if skip:
        print("Skipping Mod Quality Picker jar state apply.")
        return

    applier = resolve_quality_applier(dev_env)
    if applier is None:
        print("WARNING: Mod Quality Picker applier was not found; preset jar state was not re-applied.")
        print("         Run update-local-mods once the ModQualityPicker source checkout exists, or pass --skip-quality-apply intentionally.")
        return

    command = [sys.executable, applier, "apply", "--instance-root", minecraft_dir]
    if dry_run:
        command.append("--dry-run")

    pending_profile = quality_pending_profile_path(minecraft_dir)
    if pending_profile.exists():
        print("Applying queued Mod Quality Picker profile to synced jars...", flush=True)
    else:
        print("No queued Mod Quality Picker profile found; applying active profile to synced jars...", flush=True)
    run(command, cwd=REPO_ROOT, env=python_compat_environment())


def active_quality_profile_id(minecraft_dir: Path) -> str | None:
    config = minecraft_dir / "config" / "modqualitypicker-common.toml"
    if not config.exists():
        return None

    text = config.read_text(encoding="utf-8")
    if tomllib is not None:
        try:
            parsed = tomllib.loads(text)
            profile_id = parsed.get("activeProfileId")
            return profile_id if isinstance(profile_id, str) and profile_id else None
        except tomllib.TOMLDecodeError:
            pass

    match = re.search(r'activeProfileId\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else None


def restore_active_quality_profile_id(minecraft_dir: Path, profile_id: str | None, *, dry_run: bool) -> None:
    if not profile_id:
        return

    config = minecraft_dir / "config" / "modqualitypicker-common.toml"
    line = f'activeProfileId = "{profile_id}"'
    if dry_run:
        print(f"DRY RUN: preserve Mod Quality Picker activeProfileId = {profile_id}")
        return

    config.parent.mkdir(parents=True, exist_ok=True)
    if not config.exists():
        config.write_text(line + "\n", encoding="utf-8")
        print(f"Restored Mod Quality Picker activeProfileId = {profile_id}")
        return

    text = config.read_text(encoding="utf-8")
    if re.search(r'(?m)^\s*activeProfileId\s*=\s*"[^"]*"\s*$', text):
        next_text = re.sub(r'(?m)^\s*activeProfileId\s*=\s*"[^"]*"\s*$', line, text, count=1)
    else:
        separator = "" if text.endswith(("\n", "\r")) else "\n"
        next_text = f"{text}{separator}{line}\n"

    if next_text != text:
        config.write_text(next_text, encoding="utf-8")
        print(f"Restored Mod Quality Picker activeProfileId = {profile_id}")


def build_environment(dev_env: dict) -> dict[str, str]:
    env = os.environ.copy()
    java_home = setting(
        None,
        ("MINECRAFT_BEYOND_JAVA_HOME", "JAVA_HOME"),
        dev_env,
        "javaHome",
        None,
    )
    if java_home:
        env["JAVA_HOME"] = str(java_home)
        env["PATH"] = f"{java_home / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    return env


def java_version(java: Path) -> str:
    completed = subprocess.run(
        [str(java), "-version"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
    match = re.search(r'version "([^"]+)"', output)
    return match.group(1) if match else output.strip().splitlines()[0] if output.strip() else "unknown"


def java_major(version: str) -> int | None:
    match = re.match(r"(\d+)", version)
    if not match:
        return None
    major = int(match.group(1))
    if major == 1:
        legacy = re.match(r"1\.(\d+)", version)
        return int(legacy.group(1)) if legacy else None
    return major


def print_checks(title: str, checks: Iterable[Check]) -> bool:
    items = list(checks)
    if not items:
        return True

    print(f"\n{title}")
    width = max(len(item.name) for item in items)
    ok = True
    for item in items:
        required = " required" if item.required else ""
        detail = f" - {item.detail}" if item.detail else ""
        print(f"  {item.name.ljust(width)}  {item.status}{required}{detail}")
        if item.required and not item.ok:
            ok = False
    return ok


def command_doctor(args: argparse.Namespace) -> int:
    dev_env = load_dev_env()
    source_root = setting(
        args.source_root,
        ("MINECRAFT_MOD_SOURCE_ROOT",),
        dev_env,
        "sourceRoot",
        DEFAULT_SOURCE_ROOT,
    )
    mods_dir = setting(
        args.mods_dir,
        ("MINECRAFT_BEYOND_PRISM_MODS_DIR",),
        dev_env,
        "modsDir",
        DEFAULT_PRISM_MODS_DIR,
    )
    shaderpacks_dir = setting(
        args.shaderpacks_dir,
        ("MINECRAFT_BEYOND_PRISM_SHADERPACKS_DIR",),
        dev_env,
        "shaderpacksDir",
        DEFAULT_PRISM_SHADERPACKS_DIR,
    )
    packwiz = resolve_packwiz(dev_env, args.packwiz)
    java = resolve_java(dev_env, args.java_home)

    required_ok = True

    git_found = shutil.which("git")
    gh_found = shutil.which("gh")
    go_found = shutil.which("go")

    tool_checks = [
        Check("git", "found" if git_found else "missing", git_found or "", required=True),
        Check("gh", "found" if gh_found else "missing", gh_found or ""),
        Check("go", "found" if go_found else "missing", go_found or "needed only for install-packwiz"),
        Check("packwiz", "found" if packwiz else "missing", str(packwiz) if packwiz else "run install-packwiz or set MINECRAFT_BEYOND_PACKWIZ"),
    ]

    if java:
        version = java_version(java)
        major = java_major(version)
        status = "found" if major == 21 else "warning"
        detail = f"{java} ({version}); Java 21 is recommended for this pack"
        tool_checks.append(Check("java", status, detail, required=True))
    else:
        tool_checks.append(Check("java", "missing", "set MINECRAFT_BEYOND_JAVA_HOME or JAVA_HOME", required=True))

    required_ok = print_checks("Tools", tool_checks) and required_ok

    git_checks: list[Check] = []
    if git_found:
        branch = command_output(["git", "branch", "--show-current"])
        head = command_output(["git", "rev-parse", "--short", "HEAD"])
        dirty = command_output(["git", "status", "--porcelain"])
        git_checks.append(Check("branch", "ok", branch or "(detached)"))
        git_checks.append(Check("head", "ok", head))
        git_checks.append(Check("working tree", "clean" if not dirty else "dirty", "uncommitted changes present" if dirty else ""))
    required_ok = print_checks("Repository", git_checks) and required_ok

    metadata_checks: list[Check] = []
    if PACK_TOML.exists():
        minecraft = first_line_match(PACK_TOML, r'minecraft\s*=\s*"([^"]+)"')
        neoforge = first_line_match(PACK_TOML, r'neoforge\s*=\s*"([^"]+)"')
        metadata_checks.append(Check("minecraft", "ok" if minecraft == "1.21.1" else "warning", minecraft or "not found"))
        metadata_checks.append(Check("neoforge", "ok" if neoforge == "21.1.234" else "warning", neoforge or "not found"))
    else:
        metadata_checks.append(Check("pack.toml", "missing", str(PACK_TOML), required=True))

    expected_hash = parse_pack_index_hash()
    if expected_hash and INDEX_TOML.exists():
        actual_hash = sha256(INDEX_TOML)
        metadata_checks.append(Check("index hash", "matched" if actual_hash == expected_hash else "mismatch", actual_hash))
    else:
        metadata_checks.append(Check("index hash", "missing", "pack.toml or index.toml is incomplete", required=True))

    files = parse_index_files()
    missing_files: list[str] = []
    mismatched_files: list[str] = []
    for item in files:
        relative_file = item.get("file")
        expected_file_hash = item.get("hash")
        if not relative_file:
            continue
        path = PACK_DIR / relative_file
        if not path.exists():
            missing_files.append(relative_file)
            continue
        if expected_file_hash and sha256(path) != expected_file_hash:
            mismatched_files.append(relative_file)

    metadata_checks.append(Check("indexed files", "ok" if not missing_files else "missing", f"{len(files)} listed, {len(missing_files)} missing"))
    metadata_checks.append(Check("file hashes", "matched" if not mismatched_files else "mismatch", f"{len(mismatched_files)} mismatch(es)"))

    mod_metadata = sorted(PACK_MODS_DIR.glob("*.pw.toml"))
    shader_metadata = sorted(PACK_SHADERPACKS_DIR.glob("*.pw.toml"))
    metadata_checks.append(Check("mod metadata", "ok", f"{len(mod_metadata)} .pw.toml files"))
    metadata_checks.append(Check("shader metadata", "ok", f"{len(shader_metadata)} .pw.toml files"))
    required_ok = print_checks("Pack", metadata_checks) and required_ok

    env_checks = [
        Check("dev env file", "found" if DEV_ENV_LOCAL.exists() else "missing", str(DEV_ENV_LOCAL)),
        Check("source root", "found" if source_root and source_root.exists() else "missing", str(source_root) if source_root else ""),
        Check("Prism mods", "found" if mods_dir and mods_dir.exists() else "missing", str(mods_dir) if mods_dir else ""),
        Check("Prism shaderpacks", "found" if shaderpacks_dir and shaderpacks_dir.exists() else "missing", str(shaderpacks_dir) if shaderpacks_dir else ""),
    ]

    local_mod_checks: list[Check] = []
    local_mods = read_local_mods()
    existing = 0
    for mod in local_mods:
        source_dir = source_root / mod["sourceFolder"] if source_root else None
        if source_dir and source_dir.exists():
            existing += 1
    local_mod_checks.append(Check("local mod sources", "ok" if existing == len(local_mods) else "partial", f"{existing}/{len(local_mods)} present"))

    print_checks("Local Environment", env_checks)
    print_checks("Local Mods", local_mod_checks)

    if args.strict:
        strict_failures = [
            item
            for item in [*tool_checks, *metadata_checks]
            if item.status in {"missing", "mismatch"} or (item.required and not item.ok)
        ]
        return 1 if strict_failures or not required_ok else 0

    return 0


def command_install_packwiz(args: argparse.Namespace) -> int:
    go = shutil.which("go")
    if not go:
        raise ToolError("Go is required to install packwiz. Install Go first or put packwiz on PATH.")

    install_dir = expand_path(args.install_dir or TOOLS_DIR / "bin")
    assert install_dir is not None
    install_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["GOBIN"] = str(install_dir)
    module = args.module
    print(f"Installing {module} into {install_dir}")
    completed = subprocess.run([go, "install", module], cwd=str(REPO_ROOT), env=env, text=True)
    if completed.returncode != 0:
        return completed.returncode

    dev_env = load_dev_env()
    packwiz = resolve_packwiz(dev_env)
    if not packwiz:
        raise ToolError(f"packwiz did not appear in {install_dir}")

    print(f"packwiz installed at {packwiz}")
    return 0


def command_init_env(args: argparse.Namespace) -> int:
    if DEV_ENV_LOCAL.exists() and not args.force:
        raise ToolError(f"{DEV_ENV_LOCAL} already exists. Re-run with --force to replace it.")

    config = load_json(TOOLS_DIR / "dev-env.example.json")
    overrides = {
        "sourceRoot": args.source_root,
        "modsDir": args.mods_dir,
        "shaderpacksDir": args.shaderpacks_dir,
        "packwiz": args.packwiz,
        "javaHome": args.java_home,
    }
    for key, value in overrides.items():
        if value is not None:
            config[key] = value

    DEV_ENV_LOCAL.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {DEV_ENV_LOCAL}")
    return 0


def git(args: Sequence[str], cwd: Path, *, dry_run: bool = False, capture: bool = False) -> str:
    completed = run(["git", *args], cwd=cwd, dry_run=dry_run, capture=capture)
    return completed.stdout.strip() if capture else ""


def git_optional(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=cwd, capture=True, check=False)


def git_branch_exists(repository: Path, branch: str, dry_run: bool) -> bool:
    if dry_run:
        return True
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", branch],
        cwd=str(repository),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return completed.returncode == 0


def git_sync_row(name: str, repository: Path, *, fetch: bool = False) -> tuple[str, str, str, str, str, str, str]:
    if not repository.exists():
        return (name, "missing", "", "", "", "", str(repository))
    if not (repository / ".git").exists():
        return (name, "not-git", "", "", "", "", str(repository))

    if fetch:
        fetch_result = git_optional(["fetch", "--all", "--prune"], repository)
        if fetch_result.returncode != 0:
            detail = (fetch_result.stderr or fetch_result.stdout).strip().splitlines()
            reason = detail[-1] if detail else "fetch failed"
            return (name, "fetch-failed", "", "", "", reason, str(repository))

    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], repository, capture=True)
    head = git(["rev-parse", "--short", "HEAD"], repository, capture=True)
    dirty = git(["status", "--porcelain"], repository, capture=True)

    upstream_result = git_optional(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repository)
    upstream = upstream_result.stdout.strip() if upstream_result.returncode == 0 else ""
    ahead = behind = ""
    if upstream:
        counts = git_optional(["rev-list", "--left-right", "--count", "HEAD...@{u}"], repository)
        if counts.returncode == 0:
            parts = counts.stdout.strip().split()
            if len(parts) == 2:
                ahead, behind = parts

    flags: list[str] = []
    if dirty:
        flags.append(f"dirty:{len(dirty.splitlines())}")
    if upstream:
        if ahead and ahead != "0":
            flags.append(f"ahead:{ahead}")
        if behind and behind != "0":
            flags.append(f"behind:{behind}")
    else:
        flags.append("no-upstream")

    status = ", ".join(flags) if flags else "clean"
    remote = git_optional(["remote", "get-url", "origin"], repository)
    remote_label = remote.stdout.strip() if remote.returncode == 0 else ""
    detail = remote_label or head
    return (name, status, branch, upstream, ahead or "0", behind or "0", detail)


def command_sync_status(args: argparse.Namespace) -> int:
    if not shutil.which("git"):
        raise ToolError("git is not on PATH.")

    dev_env = load_dev_env()
    source_root = setting(
        args.source_root,
        ("MINECRAFT_MOD_SOURCE_ROOT",),
        dev_env,
        "sourceRoot",
        DEFAULT_SOURCE_ROOT,
    )
    assert source_root is not None

    repos: list[tuple[str, Path]] = [("Modpack", REPO_ROOT)]
    for mod in read_local_mods():
        repos.append((mod["name"], source_root / mod["sourceFolder"]))

    rows = [git_sync_row(name, path, fetch=args.fetch) for name, path in repos]
    print_rows(("Repo", "Status", "Branch", "Upstream", "Ahead", "Behind", "Origin or Path"), rows)

    if args.strict:
        return 1 if any(row[1] != "clean" for row in rows) else 0
    return 0


def command_update_repos(args: argparse.Namespace) -> int:
    if not shutil.which("git"):
        raise ToolError("git is not on PATH.")

    dev_env = load_dev_env()
    source_root = setting(
        args.source_root,
        ("MINECRAFT_MOD_SOURCE_ROOT",),
        dev_env,
        "sourceRoot",
        DEFAULT_SOURCE_ROOT,
    )
    assert source_root is not None

    if not args.dry_run:
        source_root.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, str, str, str]] = []
    for mod in read_local_mods():
        source_dir = source_root / mod["sourceFolder"]
        git_dir = source_dir / ".git"
        name = mod["name"]
        branch = mod["branch"]

        if not source_dir.exists():
            print(f"Cloning {name} into {source_dir}")
            git(["clone", "--branch", branch, "--single-branch", mod["repository"], str(source_dir)], REPO_ROOT, dry_run=args.dry_run)
            head = "" if args.dry_run else git(["rev-parse", "--short", "HEAD"], source_dir, capture=True)
            rows.append((name, "cloned", branch, head))
            continue

        if not git_dir.exists():
            print(f"WARNING: {name} source folder exists but is not a git repo: {source_dir}")
            rows.append((name, "skipped-not-git", branch, ""))
            continue

        dirty = "" if args.dry_run else git(["status", "--porcelain"], source_dir, capture=True)
        if dirty and not args.allow_dirty:
            print(f"WARNING: {name} has local changes. Skipping pull.")
            head = git(["rev-parse", "--short", "HEAD"], source_dir, capture=True)
            rows.append((name, "skipped-dirty", branch, head))
            continue

        current_branch = branch if args.dry_run else git(["rev-parse", "--abbrev-ref", "HEAD"], source_dir, capture=True)
        if not args.skip_pull:
            print(f"Fetching {name} {branch}")
            git(["fetch", "origin", branch], source_dir, dry_run=args.dry_run)

        if current_branch != branch:
            print(f"Switching {name} from {current_branch} to {branch}")
            if git_branch_exists(source_dir, branch, args.dry_run):
                git(["checkout", branch], source_dir, dry_run=args.dry_run)
            else:
                git(["checkout", "-b", branch, f"origin/{branch}"], source_dir, dry_run=args.dry_run)

        if not args.skip_pull:
            print(f"Pulling {name}")
            git(["pull", "--ff-only", "origin", branch], source_dir, dry_run=args.dry_run)

        head = "" if args.dry_run else git(["rev-parse", "--short", "HEAD"], source_dir, capture=True)
        rows.append((name, "checked" if args.skip_pull else "updated", branch, head))

    print_rows(("Mod", "Action", "Branch", "Head"), rows)
    return 0


def gradle_wrapper(source_dir: Path) -> list[str]:
    if os.name == "nt":
        gradlew_bat = source_dir / "gradlew.bat"
        if gradlew_bat.exists():
            return [str(gradlew_bat)]

    gradlew = source_dir / "gradlew"
    if gradlew.exists():
        if os.name != "nt" and not os.access(gradlew, os.X_OK):
            return ["bash", str(gradlew)]
        return [str(gradlew)]

    gradlew_bat = source_dir / "gradlew.bat"
    if gradlew_bat.exists():
        return [str(gradlew_bat)]

    raise ToolError(f"No Gradle wrapper found in {source_dir}")


def command_sync_local_mods(args: argparse.Namespace) -> int:
    dev_env = load_dev_env()
    source_root = setting(
        args.source_root,
        ("MINECRAFT_MOD_SOURCE_ROOT",),
        dev_env,
        "sourceRoot",
        DEFAULT_SOURCE_ROOT,
    )
    mods_dir = setting(
        args.mods_dir,
        ("MINECRAFT_BEYOND_PRISM_MODS_DIR",),
        dev_env,
        "modsDir",
        DEFAULT_PRISM_MODS_DIR,
    )
    assert source_root is not None
    assert mods_dir is not None
    build_env = build_environment(dev_env)

    if not args.dry_run:
        mods_dir.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, str, str]] = []
    missing: list[tuple[str, Path, str]] = []

    for mod in read_local_mods():
        name = mod["name"]
        source_dir = source_root / mod["sourceFolder"]
        if not source_dir.exists():
            missing.append((name, source_dir, f'git clone --branch {mod["branch"]} {mod["repository"]} "{source_dir}"'))
            continue

        if args.build:
            print(f"Building {name}...")
            run([*gradle_wrapper(source_dir), "build"], cwd=source_dir, dry_run=args.dry_run, env=build_env)

        libs_dir = source_dir / "build" / "libs"
        if not libs_dir.exists():
            if args.dry_run:
                print(f"WARNING: Would sync {name}, but {libs_dir} does not exist.")
                continue
            raise ToolError(f"No build/libs folder found for {name}. Run with --build or build the mod first.")

        jars = sorted(
            (
                jar
                for jar in libs_dir.glob(mod["jarGlob"])
                if not re.search(r"(sources|javadoc|dev|plain)", jar.name)
            ),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not jars:
            if args.dry_run:
                print(f"WARNING: Would sync {name}, but no runtime jar matching {mod['jarGlob']} exists in {libs_dir}.")
                continue
            raise ToolError(f"No runtime jar matching {mod['jarGlob']} found for {name} in {libs_dir}.")

        jar = jars[0]
        destination = local_mod_sync_destination(mods_dir, mod["modId"])
        print(f"Syncing {name}: {jar.name} -> {destination}")
        if not args.dry_run:
            shutil.copy2(jar, destination)
        rows.append((name, jar.name, str(destination)))

    if missing:
        print("\nMissing local mod source folders:")
        print_rows(("Mod", "Path", "Clone"), missing)
    if rows:
        print("\nSynced local mods:")
        print_rows(("Mod", "Jar", "Destination"), rows)
    apply_quality_profile_after_sync(dev_env, mods_dir.parent, dry_run=args.dry_run, skip=args.skip_quality_apply)
    return 0


def local_mod_sync_destination(mods_dir: Path, mod_id: str) -> Path:
    enabled = mods_dir / f"{mod_id}-local.jar"
    disabled = enabled.with_name(enabled.name + ".disabled")
    if disabled.exists() and not enabled.exists():
        return disabled
    return enabled


def command_update_local_mods(args: argparse.Namespace) -> int:
    if not args.skip_pull:
        update_args = argparse.Namespace(
            source_root=args.source_root,
            skip_pull=False,
            allow_dirty=args.allow_dirty,
            dry_run=args.dry_run,
        )
        command_update_repos(update_args)
    else:
        print("Skipping local mod repository pulls.")

    sync_args = argparse.Namespace(
        source_root=args.source_root,
        mods_dir=args.mods_dir,
        build=not args.skip_build,
        dry_run=args.dry_run,
        skip_quality_apply=args.skip_quality_apply,
    )
    command_sync_local_mods(sync_args)
    print("Local mod update complete.")
    return 0


def command_import_prism_mods(args: argparse.Namespace) -> int:
    dev_env = load_dev_env()
    prism_mods = setting(
        args.prism_mods_dir,
        ("MINECRAFT_BEYOND_PRISM_MODS_DIR",),
        dev_env,
        "modsDir",
        DEFAULT_PRISM_MODS_DIR,
    )
    pack_dir = expand_path(args.pack_dir or PACK_DIR)
    assert prism_mods is not None
    assert pack_dir is not None

    pack_toml = pack_dir / "pack.toml"
    if not pack_toml.exists():
        raise ToolError(f"pack.toml not found at {pack_toml}")

    if not prism_mods.exists():
        print(f"WARNING: Prism mods folder does not exist yet: {prism_mods}")
        return 0

    prism_jars = sorted(prism_mods.glob("*.jar"))
    if not args.include_local:
        prism_jars = [jar for jar in prism_jars if not jar.name.endswith("-local.jar")]

    if not prism_jars:
        print("No Prism mod jars found to import.")
        return 0

    print(f"Preparing to import {len(prism_jars)} Prism mod jar(s) through packwiz CurseForge detection.")
    pack_mods = pack_dir / "mods"
    packwiz = None if args.dry_run else resolve_packwiz(dev_env, args.packwiz)
    if not args.dry_run and not packwiz:
        raise ToolError("packwiz was not found. Run install-packwiz or set MINECRAFT_BEYOND_PACKWIZ.")

    if not args.dry_run:
        pack_mods.mkdir(parents=True, exist_ok=True)

    staged: list[tuple[Path, Path]] = []
    for jar in prism_jars:
        destination = pack_mods / jar.name
        print(f"Staging {jar.name}")
        if not args.dry_run:
            shutil.copy2(jar, destination)
        staged.append((jar, destination))

    if args.dry_run:
        print("Dry run complete. No files were copied and packwiz was not run.")
        return 0

    assert packwiz is not None
    print("Running packwiz cf detect...")
    run([packwiz, "cf", "detect"], cwd=pack_dir)

    unmatched = [(source, staged_path) for source, staged_path in staged if staged_path.exists()]
    if unmatched:
        print("WARNING: packwiz did not match every staged jar.")
        print_rows(("Jar", "Source"), [(path.name, str(source)) for source, path in unmatched])
        if not args.keep_unmatched_staged_jars:
            for _, staged_path in unmatched:
                staged_path.unlink()
            print("Removed unmatched staged jar copies from pack/mods. Original Prism jars were left alone.")

    print("Refreshing packwiz index...", flush=True)
    run([packwiz, "refresh"], cwd=pack_dir)
    print("Import complete. Review and commit the generated pack metadata.")
    return 0


def command_import_prism_shaderpacks(args: argparse.Namespace) -> int:
    dev_env = load_dev_env()
    prism_shaderpacks = setting(
        args.prism_shaderpacks_dir,
        ("MINECRAFT_BEYOND_PRISM_SHADERPACKS_DIR",),
        dev_env,
        "shaderpacksDir",
        DEFAULT_PRISM_SHADERPACKS_DIR,
    )
    pack_dir = expand_path(args.pack_dir or PACK_DIR)
    assert prism_shaderpacks is not None
    assert pack_dir is not None

    pack_toml = pack_dir / "pack.toml"
    if not pack_toml.exists():
        raise ToolError(f"pack.toml not found at {pack_toml}")

    if not prism_shaderpacks.exists():
        print(f"WARNING: Prism shaderpacks folder does not exist yet: {prism_shaderpacks}")
        return 0

    source_metadata = sorted(prism_shaderpacks.glob("*.pw.toml"))
    if not source_metadata:
        print(f"No packwiz shader metadata found in {prism_shaderpacks}.")
        print("Install shaders through Prism or packwiz first so the repo can track metadata instead of zip files.")
        return 0

    pack_shaderpacks = pack_dir / "shaderpacks"
    if not args.dry_run:
        pack_shaderpacks.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, str, str]] = []
    managed_archives: set[str] = set()
    for metadata in source_metadata:
        normalized_metadata = normalize_shader_metadata(metadata.read_text(encoding="utf-8"))
        archive_name = packwiz_metadata_filename(metadata) or ""
        if archive_name:
            managed_archives.add(archive_name)

        destination = pack_shaderpacks / metadata.name
        if destination.exists() and destination.read_text(encoding="utf-8") == normalized_metadata:
            action = "unchanged"
        elif destination.exists():
            action = "would update" if args.dry_run else "updated"
            if not args.dry_run:
                destination.write_text(normalized_metadata, encoding="utf-8")
        else:
            action = "would copy" if args.dry_run else "copied"
            if not args.dry_run:
                destination.write_text(normalized_metadata, encoding="utf-8")
        rows.append((metadata.name, action, archive_name or "(filename not found)"))

    print_rows(("Metadata", "Action", "Archive"), rows)

    unmanaged_archives = sorted(
        archive.name for archive in prism_shaderpacks.glob("*.zip") if archive.name not in managed_archives
    )
    if unmanaged_archives:
        print("\nWARNING: These shader zip files do not have matching packwiz metadata and were not copied:")
        print_rows(("Archive",), [(name,) for name in unmanaged_archives])

    extracted_folders = sorted(
        path.name
        for path in prism_shaderpacks.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )
    if extracted_folders:
        print("\nIgnoring extracted shaderpack folders. Keep the packwiz pack focused on downloadable archives/metadata:")
        print_rows(("Folder",), [(name,) for name in extracted_folders])

    if args.skip_refresh:
        print("Skipping packwiz refresh.")
        return 0

    if args.dry_run:
        print("DRY RUN: packwiz refresh would run.")
        return 0

    packwiz = resolve_packwiz(dev_env, args.packwiz)
    if not packwiz:
        raise ToolError("packwiz was not found. Run install-packwiz or set MINECRAFT_BEYOND_PACKWIZ.")

    print("Refreshing packwiz index...", flush=True)
    run([packwiz, "refresh"], cwd=pack_dir)
    print("Shaderpack import complete. Review and commit the generated pack metadata.")
    return 0


def command_update_prism_shaderpacks(args: argparse.Namespace) -> int:
    print("Applying packwiz metadata to Prism; shaderpacks update through the same installer path as mods and configs.")
    return command_update_prism_mods(args)


def command_update_prism_mods(args: argparse.Namespace) -> int:
    dev_env = load_dev_env()
    packwiz = resolve_packwiz(dev_env, args.packwiz)
    if not packwiz:
        raise ToolError("packwiz was not found. Run install-packwiz or set MINECRAFT_BEYOND_PACKWIZ.")

    java = resolve_java(dev_env, args.java_home)
    if not java:
        raise ToolError("Java was not found. Install Java 21 or set MINECRAFT_BEYOND_JAVA_HOME/JAVA_HOME.")

    pack_dir = expand_path(args.pack_dir or PACK_DIR)
    assert pack_dir is not None
    pack_toml = pack_dir / "pack.toml"
    if not pack_toml.exists():
        raise ToolError(f"pack.toml not found at {pack_toml}")

    prism_mods = setting(
        args.mods_dir,
        ("MINECRAFT_BEYOND_PRISM_MODS_DIR",),
        dev_env,
        "modsDir",
        DEFAULT_PRISM_MODS_DIR,
    )
    minecraft_dir = expand_path(args.minecraft_dir) if args.minecraft_dir else (prism_mods.parent if prism_mods else None)
    if minecraft_dir is None:
        raise ToolError("Could not resolve the Prism minecraft directory.")
    preserved_quality_profile_id = active_quality_profile_id(minecraft_dir)

    bootstrap = setting(
        args.installer,
        ("MINECRAFT_BEYOND_PACKWIZ_INSTALLER_BOOTSTRAP",),
        dev_env,
        "packwizInstallerBootstrap",
        PACKWIZ_INSTALLER_BOOTSTRAP,
    )
    main_jar = setting(
        args.main_jar,
        ("MINECRAFT_BEYOND_PACKWIZ_INSTALLER_MAIN",),
        dev_env,
        "packwizInstallerMain",
        PACKWIZ_INSTALLER_MAIN,
    )
    assert bootstrap is not None
    assert main_jar is not None

    if not bootstrap.exists():
        if args.no_download:
            raise ToolError(f"packwiz installer bootstrap was not found at {bootstrap}")
        print(f"Downloading packwiz installer bootstrap to {bootstrap}", flush=True)
        download_file(args.bootstrap_url, bootstrap, dry_run=args.dry_run)

    port = args.port or (42123 if args.dry_run else find_free_local_port())
    pack_url = f"http://127.0.0.1:{port}/pack.toml"
    installer_command = [
        java,
        "-jar",
        bootstrap,
        "--bootstrap-main-jar",
        main_jar,
        "-g",
        pack_url,
    ]

    if args.dry_run:
        print(f"DRY RUN: ensure Prism minecraft dir exists: {minecraft_dir}")
        print(f"DRY RUN: ({pack_dir}) {packwiz} serve --port {port}")
        print(f"DRY RUN: ({minecraft_dir}) {' '.join(str(part) for part in installer_command)}")
        restore_active_quality_profile_id(minecraft_dir, preserved_quality_profile_id, dry_run=True)
        apply_quality_profile_after_sync(dev_env, minecraft_dir, dry_run=True, skip=args.skip_quality_apply)
        return 0

    minecraft_dir.mkdir(parents=True, exist_ok=True)
    (minecraft_dir / "mods").mkdir(parents=True, exist_ok=True)

    print(f"Serving local packwiz metadata from {pack_dir}", flush=True)
    server = subprocess.Popen(
        [str(packwiz), "serve", "--port", str(port)],
        cwd=str(pack_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_http(pack_url, server)
        print(f"Updating Prism instance at {minecraft_dir}", flush=True)
        run(installer_command, cwd=minecraft_dir)
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)

    print("Prism pack files updated from packwiz metadata.")
    restore_active_quality_profile_id(minecraft_dir, preserved_quality_profile_id, dry_run=False)
    apply_quality_profile_after_sync(dev_env, minecraft_dir, dry_run=False, skip=args.skip_quality_apply)
    return 0


def command_refresh(args: argparse.Namespace) -> int:
    dev_env = load_dev_env()
    packwiz = resolve_packwiz(dev_env, args.packwiz)
    if not packwiz:
        raise ToolError("packwiz was not found. Run install-packwiz or set MINECRAFT_BEYOND_PACKWIZ.")
    pack_dir = expand_path(args.pack_dir or PACK_DIR)
    assert pack_dir is not None
    run([packwiz, "refresh"], cwd=pack_dir)
    return 0


def print_rows(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    materialized = [[str(cell) for cell in row] for row in rows]
    if not materialized:
        return
    widths = [len(header) for header in headers]
    for row in materialized:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    print("  " + "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  " + "  ".join("-" * width for width in widths))
    for row in materialized:
        print("  " + "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))


def add_update_prism_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--minecraft-dir", help="Prism minecraft folder. Defaults to the parent of modsDir.")
    command.add_argument("--mods-dir", help="Prism mods folder, used to derive minecraft-dir when minecraft-dir is omitted.")
    command.add_argument("--pack-dir")
    command.add_argument("--packwiz")
    command.add_argument("--java-home")
    command.add_argument("--installer", help="Path to packwiz-installer-bootstrap.jar.")
    command.add_argument("--main-jar", help="Path where the bootstrapper stores packwiz-installer.jar.")
    command.add_argument("--bootstrap-url", default=PACKWIZ_INSTALLER_BOOTSTRAP_URL)
    command.add_argument("--no-download", action="store_true", help="Fail instead of downloading the bootstrap jar if it is missing.")
    command.add_argument("--port", type=int, help="Local port for the temporary packwiz server.")
    command.add_argument("--skip-quality-apply", action="store_true", help="Do not re-apply the active Mod Quality Picker preset after packwiz sync.")
    command.add_argument("--dry-run", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="modpack",
        description="Cross-platform Minecraft Beyond workspace tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check the local workspace and pack metadata.")
    doctor.add_argument("--strict", action="store_true", help="Exit non-zero for missing required tools or pack hash mismatches.")
    doctor.add_argument("--source-root")
    doctor.add_argument("--mods-dir")
    doctor.add_argument("--shaderpacks-dir")
    doctor.add_argument("--packwiz")
    doctor.add_argument("--java-home")
    doctor.set_defaults(func=command_doctor)

    install = subparsers.add_parser("install-packwiz", help="Install packwiz into tools/bin using Go.")
    install.add_argument("--install-dir")
    install.add_argument("--module", default="github.com/packwiz/packwiz@latest")
    install.set_defaults(func=command_install_packwiz)

    init_env = subparsers.add_parser("init-env", help="Create the ignored machine-local dev environment config.")
    init_env.add_argument("--source-root")
    init_env.add_argument("--mods-dir")
    init_env.add_argument("--shaderpacks-dir")
    init_env.add_argument("--packwiz")
    init_env.add_argument("--java-home")
    init_env.add_argument("--force", action="store_true")
    init_env.set_defaults(func=command_init_env)

    sync_status = subparsers.add_parser("sync-status", help="Show dirty/ahead/behind status for the pack and local mod repos.")
    sync_status.add_argument("--source-root")
    sync_status.add_argument("--fetch", action="store_true", help="Fetch remotes before calculating ahead/behind counts.")
    sync_status.add_argument("--strict", action="store_true", help="Exit non-zero unless every repo is clean and synced.")
    sync_status.set_defaults(func=command_sync_status)

    update_repos = subparsers.add_parser("update-repos", help="Clone or fast-forward local mod repositories.")
    update_repos.add_argument("--source-root")
    update_repos.add_argument("--skip-pull", action="store_true")
    update_repos.add_argument("--allow-dirty", action="store_true")
    update_repos.add_argument("--dry-run", action="store_true")
    update_repos.set_defaults(func=command_update_repos)

    sync = subparsers.add_parser("sync-local-mods", help="Copy built local mod jars into the Prism mods folder.")
    sync.add_argument("--source-root")
    sync.add_argument("--mods-dir")
    sync.add_argument("--build", action="store_true")
    sync.add_argument("--skip-quality-apply", action="store_true", help="Do not re-apply the active Mod Quality Picker preset after syncing jars.")
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(func=command_sync_local_mods)

    update = subparsers.add_parser("update-local-mods", help="Pull, build, and sync local mod jars.")
    update.add_argument("--source-root")
    update.add_argument("--mods-dir")
    update.add_argument("--skip-pull", action="store_true")
    update.add_argument("--skip-build", action="store_true")
    update.add_argument("--allow-dirty", action="store_true")
    update.add_argument("--skip-quality-apply", action="store_true", help="Do not re-apply the active Mod Quality Picker preset after syncing jars.")
    update.add_argument("--dry-run", action="store_true")
    update.set_defaults(func=command_update_local_mods)

    prism = subparsers.add_parser("import-prism-mods", help="Import Prism-downloaded jars through packwiz CurseForge detection.")
    prism.add_argument("--prism-mods-dir")
    prism.add_argument("--pack-dir")
    prism.add_argument("--packwiz")
    prism.add_argument("--include-local", action="store_true")
    prism.add_argument("--keep-unmatched-staged-jars", action="store_true")
    prism.add_argument("--dry-run", action="store_true")
    prism.set_defaults(func=command_import_prism_mods)

    prism_shaders = subparsers.add_parser("import-prism-shaderpacks", help="Import Prism shaderpack metadata into packwiz.")
    prism_shaders.add_argument("--prism-shaderpacks-dir")
    prism_shaders.add_argument("--pack-dir")
    prism_shaders.add_argument("--packwiz")
    prism_shaders.add_argument("--skip-refresh", action="store_true")
    prism_shaders.add_argument("--dry-run", action="store_true")
    prism_shaders.set_defaults(func=command_import_prism_shaderpacks)

    update_prism = subparsers.add_parser("update-prism-mods", help="Apply packwiz metadata to the Prism minecraft folder.")
    add_update_prism_arguments(update_prism)
    update_prism.set_defaults(func=command_update_prism_mods)

    update_prism_shaders = subparsers.add_parser("update-prism-shaderpacks", help="Apply packwiz shaderpack metadata to Prism.")
    add_update_prism_arguments(update_prism_shaders)
    update_prism_shaders.set_defaults(func=command_update_prism_shaderpacks)

    refresh = subparsers.add_parser("refresh", help="Run packwiz refresh for the pack.")
    refresh.add_argument("--pack-dir")
    refresh.add_argument("--packwiz")
    refresh.set_defaults(func=command_refresh)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ToolError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
