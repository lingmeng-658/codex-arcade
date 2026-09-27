import unittest
from unittest.mock import patch

from codex_arcade.i18n import language_from_ui_locale, saved_or_system_language, text


class I18nTests(unittest.TestCase):
    def test_has_natural_chinese_and_english_status(self):
        self.assertEqual(text("working", "en"), "Codex is working. Your turn to play.")
        self.assertEqual(text("working", "zh-CN"), "Codex 正在干活 · 你先摸会儿鱼")

    def test_only_simplified_chinese_ui_locale_uses_chinese(self):
        self.assertEqual(language_from_ui_locale("zh-CN"), "zh-CN")
        self.assertEqual(language_from_ui_locale("zh-TW"), "en")
        self.assertEqual(language_from_ui_locale("en-US"), "en")

    def test_saved_language_takes_precedence_over_detection(self):
        with patch("codex_arcade.i18n.system_language", return_value="en"):
            self.assertEqual(saved_or_system_language("zh-CN"), "zh-CN")
