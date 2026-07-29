import json
import tomllib
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "pack"


class Stage2DistributionTests(unittest.TestCase):
    def test_client_distribution_does_not_advertise_a_server(self) -> None:
        config = PACK / "config" / "modqualitypicker-common.toml"
        parsed = tomllib.loads(config.read_text(encoding="utf-8"))
        self.assertIn("serverEnvironmentEndpoint", parsed)
        self.assertEqual(parsed["serverEnvironmentEndpoint"], "")

    def test_mod_and_gate_artifacts_are_identical(self) -> None:
        mod = PACK / "mods" / "modqualitypicker-local.jar"
        helper = (
            PACK
            / "config"
            / "modqualitypicker"
            / "launcher"
            / "modqualitypicker-bootstrap.jar"
        )
        self.assertTrue(mod.is_file())
        self.assertTrue(helper.is_file())
        self.assertEqual(mod.read_bytes(), helper.read_bytes())

    def test_bundled_jar_contains_stage2_entry_points(self) -> None:
        mod = PACK / "mods" / "modqualitypicker-local.jar"
        expected_classes = {
            "org/destroyermob/modqualitypicker/client/"
            "ClientEnvironmentHandshake.class",
            "org/destroyermob/modqualitypicker/client/"
            "EnvironmentJoinPreflight.class",
            "org/destroyermob/modqualitypicker/client/"
            "ServerEnvironmentStatusProbe.class",
            "org/destroyermob/modqualitypicker/environment/"
            "DiscoveryObservationStore.class",
            "org/destroyermob/modqualitypicker/environment/"
            "Stage2HandshakePolicy.class",
            "org/destroyermob/modqualitypicker/mixin/"
            "ConnectScreenMixin.class",
            "org/destroyermob/modqualitypicker/mixin/"
            "MinecraftServerStatusMixin.class",
            "org/destroyermob/modqualitypicker/network/"
            "EnvironmentNetwork.class",
        }
        with zipfile.ZipFile(mod) as archive:
            names = set(archive.namelist())
            self.assertTrue(expected_classes.issubset(names))
            mixins = json.loads(
                archive.read("modqualitypicker.mixins.json")
            )
            self.assertIn(
                "MinecraftServerStatusMixin",
                mixins["mixins"],
            )
            self.assertIn("ConnectScreenMixin", mixins["client"])
            language = json.loads(
                archive.read(
                    "assets/modqualitypicker/lang/en_us.json"
                )
            )
            self.assertIn(
                "modqualitypicker.discovery.required_title",
                language,
            )
            self.assertIn(
                "modqualitypicker.discovery.join_anyway",
                language,
            )


if __name__ == "__main__":
    unittest.main()
