import unittest

from codex_arcade.hooks import add_arcade_hooks, remove_arcade_hooks


class HooksTests(unittest.TestCase):
    def test_add_and_remove_preserves_existing_hooks(self):
        existing = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "keep.cmd"}]}]}}
        installed = add_arcade_hooks(existing, r"C:\Arcade\start_arcade.cmd", r"C:\Arcade\stop_arcade.cmd")
        self.assertEqual(len(installed["hooks"]["Stop"]), 2)
        self.assertIn("UserPromptSubmit", installed["hooks"])
        removed = remove_arcade_hooks(installed)
        self.assertEqual(removed["hooks"]["Stop"], existing["hooks"]["Stop"])
        self.assertNotIn("UserPromptSubmit", removed["hooks"])
