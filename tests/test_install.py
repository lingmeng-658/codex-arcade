import tempfile
import unittest
from pathlib import Path

from install import install
from uninstall import uninstall


class InstallerTests(unittest.TestCase):
    def test_install_and_uninstall_keep_existing_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / ".codex"
            codex.mkdir()
            hooks = codex / "hooks.json"
            hooks.write_text('{"hooks":{"Stop":[{"hooks":[{"command":"keep.cmd"}]}]}}', encoding="utf-8")
            install(source=Path.cwd(), local_app_data=root / "local", codex_home=codex, dry_run=False)
            self.assertIn("Codex Arcade", hooks.read_text(encoding="utf-8"))
            uninstall(local_app_data=root / "local", codex_home=codex, keep_data=True)
            self.assertIn("keep.cmd", hooks.read_text(encoding="utf-8"))
