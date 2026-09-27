import copy

MARKER = "Codex Arcade v0.1"


def _entry(command: str) -> dict:
    return {"hooks": [{"type": "command", "command": command, "commandWindows": command,
                        "timeout": 8, "codexArcade": MARKER}]}


def add_arcade_hooks(config: dict, start_cmd: str, stop_cmd: str) -> dict:
    result = copy.deepcopy(config); hooks = result.setdefault("hooks", {})
    entries = {"UserPromptSubmit": start_cmd, "Stop": stop_cmd, "Interrupt": stop_cmd}
    for event, command in entries.items():
        groups = hooks.setdefault(event, [])
        if not any(any(h.get("codexArcade") == MARKER for h in group.get("hooks", [])) for group in groups):
            groups.append(_entry(command))
    return result


def remove_arcade_hooks(config: dict) -> dict:
    result = copy.deepcopy(config); hooks = result.get("hooks", {})
    for event in list(hooks):
        kept = []
        for group in hooks[event]:
            remaining = [hook for hook in group.get("hooks", []) if hook.get("codexArcade") != MARKER]
            if remaining:
                group["hooks"] = remaining
                kept.append(group)
        if kept: hooks[event] = kept
        else: hooks.pop(event)
    return result
