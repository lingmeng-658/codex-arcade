import argparse
import json
import os
import shutil
from pathlib import Path

from codex_arcade.hooks import remove_arcade_hooks
from codex_arcade.stats import atomic_json


def uninstall(local_app_data=None, codex_home=None, keep_data=True):
    local_app_data=Path(local_app_data or os.environ.get("LOCALAPPDATA",Path.home())) / "CodexArcade" if local_app_data is None else Path(local_app_data)
    codex_home=Path(codex_home or Path.home()/".codex"); hooks_file=codex_home/"hooks.json"
    if hooks_file.exists():
        config=json.loads(hooks_file.read_text(encoding="utf-8")); atomic_json(hooks_file,remove_arcade_hooks(config))
    app=local_app_data/"app"
    if app.exists():shutil.rmtree(app)
    if not keep_data and local_app_data.exists():shutil.rmtree(local_app_data)


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--delete-data",action="store_true");args=parser.parse_args();uninstall(keep_data=not args.delete_data);print("Codex Arcade hooks removed. Local statistics were " + ("kept." if not args.delete_data else "deleted."))
