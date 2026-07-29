from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import modpack


class Stage1MaintenanceGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="mqp-pack-tool-test-")
        self.minecraft = Path(self.temporary.name)
        self.mods = self.minecraft / "mods"
        self.intent = (
            self.minecraft
            / "config"
            / "modqualitypicker"
            / "server-environments"
            / "state"
            / "intents"
            / "current.json"
        )
        self.active = self.intent.parents[1] / "active-environment.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_intent(self, state: str) -> None:
        self.intent.parent.mkdir(parents=True, exist_ok=True)
        self.intent.write_text(json.dumps({"state": state}), encoding="utf-8")

    def test_released_or_absent_state_allows_maintenance(self) -> None:
        modpack.assert_server_environment_released(self.minecraft)
        for state in sorted(modpack.RELEASED_ENVIRONMENT_STATES):
            self.write_intent(state)
            modpack.assert_server_environment_released(self.minecraft)

    def test_active_nonterminal_and_corrupt_state_fail_closed(self) -> None:
        self.write_intent("COMPLETED")
        with self.assertRaises(modpack.ToolError):
            modpack.assert_server_environment_released(self.minecraft)

        self.write_intent("RESTORED")
        self.active.parent.mkdir(parents=True, exist_ok=True)
        self.active.write_text("{}", encoding="utf-8")
        with self.assertRaises(modpack.ToolError):
            modpack.assert_server_environment_released(self.minecraft)

        self.active.unlink()
        self.intent.write_text("{", encoding="utf-8")
        with self.assertRaises(modpack.ToolError):
            modpack.assert_server_environment_released(self.minecraft)

    def test_sync_refuses_before_copying_any_mod(self) -> None:
        self.write_intent("VERIFYING_LAUNCH")
        args = argparse.Namespace(
            mods_dir=str(self.mods),
            mod=["ecology"],
            skip_quality_apply=True,
            dry_run=False,
        )
        with mock.patch.object(
            modpack,
            "_command_sync_local_mods_locked",
            return_value=0,
        ) as inner:
            with self.assertRaises(modpack.ToolError):
                modpack.command_sync_local_mods(args)
            inner.assert_not_called()

    def test_packwiz_update_refuses_before_installer(self) -> None:
        self.write_intent("CONNECTED")
        args = argparse.Namespace(
            minecraft_dir=str(self.minecraft),
            mods_dir=None,
            skip_quality_apply=True,
            dry_run=False,
        )
        with mock.patch.object(
            modpack,
            "_command_update_prism_mods_locked",
            return_value=0,
        ) as inner:
            with self.assertRaises(modpack.ToolError):
                modpack.command_update_prism_mods(args)
            inner.assert_not_called()

    def test_distribution_paths_cover_mod_and_stable_helper(self) -> None:
        mod_path, helper_path = modpack.packed_quality_jar_paths()
        self.assertEqual(mod_path, modpack.PACK_DIR / "mods" / "modqualitypicker-local.jar")
        self.assertEqual(
            helper_path,
            modpack.PACK_DIR
            / "config"
            / "modqualitypicker"
            / "launcher"
            / "modqualitypicker-bootstrap.jar",
        )


if __name__ == "__main__":
    unittest.main()
