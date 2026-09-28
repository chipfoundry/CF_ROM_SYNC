import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "program_cf_rom_sync.py"
# Split so this file does not itself contain the private names it rejects.
BANNED = (
    "s" + "8srom",
    "s" + "8",
    "infin" + "eon",
    "cyp" + "ress",
    "ps" + "oc",
    "m0" + "s" + "8",
    "ro" + "mb",
    "cp" + "rog",
)


def load_script():
    spec = importlib.util.spec_from_file_location("program_cf_rom_sync", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProgramCfRomSyncTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_script()

    def test_image_must_be_1024_bytes(self):
        with self.assertRaises(SystemExit):
            self.module.parse_image("aa\n", "image.hex")

    def test_outputs_carry_the_image_and_no_internal_names(self):
        data = [0] * 1024
        data[0] = 0xA5
        data[1023] = 0x5A
        sim = self.module.emit_sim(data)
        lvs = self.module.emit_lvs(data)
        digest = self.module.image_sha256(data)
        self.assertIn("mem[0] = 8'ha5;", sim)
        self.assertIn("mem[1023] = 8'h5a;", sim)
        self.assertIn("module CF_ROM_SYNC_core", sim)
        self.assertIn("module CF_ROM_SYNC ", sim)
        self.assertIn(digest, sim)
        self.assertIn(digest, lvs)
        self.assertIn("module CF_ROM_SYNC_core", lvs)
        self.assertNotIn("mem[", lvs)
        blob = "\n".join(
            [
                SCRIPT.read_text(),
                (ROOT / "doc" / "PROGRAMMING.md").read_text(),
                sim,
                lvs,
                self.module.normalized_image(data),
            ]
        ).lower()
        for word in BANNED:
            self.assertNotIn(word, blob)

    def test_command_writes_the_three_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "image.hex"
            image.write_text("\n".join(["00"] * 1023 + ["ff"]) + "\n")
            sim = Path(tmp) / "sim.v"
            lvs = Path(tmp) / "lvs.v"
            rom = Path(tmp) / "CF_ROM_SYNC.rom"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(image),
                    "--sim",
                    str(sim),
                    "--lvs",
                    str(lvs),
                    "--image-out",
                    str(rom),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("bytes 1024 sha256", result.stdout)
            self.assertTrue(sim.is_file() and lvs.is_file() and rom.is_file())
            self.assertEqual(len(rom.read_text().splitlines()), 1024)
            self.assertEqual(rom.read_text().splitlines()[-1], "ff")


if __name__ == "__main__":
    unittest.main()
