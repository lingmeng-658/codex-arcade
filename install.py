import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from codex_arcade.hooks import add_arcade_hooks
from codex_arcade.stats import atomic_json


def command(path: Path) -> str:
    return f'cmd.exe /d /s /c "{path}"'


def install(source=None, local_app_data=None, codex_home=None, dry_run=False):
    source = Path(source or Path(__file__).parent).resolve()
    local_app_data = Path(local_app_data or os.environ.get("LOCALAPPDATA", Path.home())) / "CodexArcade" if local_app_data is None else Path(local_app_data)
    codex_home = Path(codex_home or Path.home() / ".codex")
    if not (sys.version_info >= (3, 10)):
        raise RuntimeError("Codex Arcade requires Python 3.10 or newer. Install Python from python.org, then run install.py again.")
    try:
        import tkinter  # noqa: F401
    except ImportError as error:
        raise RuntimeError("tkinter is unavailable. Reinstall Python with the Tcl/Tk option enabled.") from error
    launcher = shutil.which("py")
    target = local_app_data / "app"; hooks_file = codex_home / "hooks.json"
    if dry_run:return {"target": str(target), "hooks": str(hooks_file), "python": sys.executable,
                       "py_launcher": launcher or "not found (the cmd launchers will use python)", "would_copy": True}
    local_app_data.mkdir(parents=True, exist_ok=True); target.mkdir(parents=True, exist_ok=True)
    for item in ("codex_arcade", "start.py", "stop.py", "start_arcade.cmd", "stop_arcade.cmd"):
        src=source/item;dst=target/item
        if src.is_dir(): shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else: shutil.copy2(src,dst)
    codex_home.mkdir(parents=True, exist_ok=True)
    config={}
    if hooks_file.exists():
        backup=hooks_file.with_name("hooks.json.codex-arcade-backup")
        shutil.copy2(hooks_file,backup)
        try: config=json.loads(hooks_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError: raise RuntimeError(f"{hooks_file} is not valid JSON; installation did not change it.")
    config=add_arcade_hooks(config,command(target/"start_arcade.cmd"),command(target/"stop_arcade.cmd"));atomic_json(hooks_file,config)
    return {"target":str(target),"hooks":str(hooks_file),"backup":str(hooks_file.with_name("hooks.json.codex-arcade-backup"))}


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--dry-run",action="store_true");args=parser.parse_args()
    try:
        result=install(dry_run=args.dry_run)
        print("Dry run:" if args.dry_run else "Installed Codex Arcade.")
        for key,value in result.items():print(f"{key}: {value}")
        if not args.dry_run: print("Open Codex Desktop → Settings → Hooks and review/approve the new Codex Arcade hooks before first use.")
    except RuntimeError as error: print(f"Install failed: {error}",file=sys.stderr);raise SystemExit(1)
