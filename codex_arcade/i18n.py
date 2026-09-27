import ctypes
import sys


STRINGS = {
    "en": {
        "title": "CODEX ARCADE", "working": "Codex is working. Your turn to play.",
        "finished": "CODEX HAS FINISHED.", "back": "BACK TO WORK.", "random": "Random",
        "random_next": "Random", "games": "Games", "restart": "Restart", "paused": "PAUSED", "game_over": "GAME OVER", "game_controls": "P/Space Pause · R Restart · Tab/G Games · N Random · Esc Close", "stats": "Stats", "language": "Language", "today": "Arcade Time Today",
        "tasks": "Tasks Completed", "total": "Total Arcade Time", "score": "Score",
        "controls": "WASD / arrows · Esc to close", "snake": "Snake", "dodge": "Dodge",
        "aim": "Aim Trainer", "breakout": "Breakout", "pong": "Pong", "best": "Best",
        "longest": "Longest", "close": "Close", "home": "Home",
    },
    "zh-CN": {
        "title": "CODEX ARCADE", "working": "Codex 正在干活 · 你先摸会儿鱼",
        "finished": "CODEX 干完了。", "back": "别玩了，回来上班。", "random": "随机",
        "random_next": "随机", "games": "游戏", "restart": "重开", "paused": "已暂停", "game_over": "本局结束", "game_controls": "P/空格 暂停 · R 重开 · Tab/G 游戏 · N 随机 · Esc 关闭", "stats": "统计", "language": "语言", "today": "今日摸鱼",
        "tasks": "Codex 完成任务", "total": "累计摸鱼", "score": "得分",
        "controls": "WASD / 方向键 · Esc 退出", "snake": "贪吃蛇", "dodge": "躲避",
        "aim": "瞄准训练", "breakout": "打砖块", "pong": "乒乓", "best": "最高",
        "longest": "最长", "close": "关闭", "home": "首页",
    },
}


def language_from_ui_locale(locale_name: str) -> str:
    return "zh-CN" if locale_name.replace("_", "-").lower() == "zh-cn" else "en"


def _windows_ui_locale_name() -> str:
    if sys.platform != "win32":
        return ""
    try:
        language_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        buffer = ctypes.create_unicode_buffer(85)
        if ctypes.windll.kernel32.LCIDToLocaleName(language_id, buffer, len(buffer), 0):
            return buffer.value
    except Exception:
        pass
    return ""


def system_language() -> str:
    return language_from_ui_locale(_windows_ui_locale_name())


def saved_or_system_language(saved_language: str) -> str:
    return language_from_ui_locale(saved_language) if saved_language else system_language()


def text(key: str, language: str = "en") -> str:
    return STRINGS.get(language, STRINGS["en"]).get(key, key)
