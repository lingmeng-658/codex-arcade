import argparse
from codex_arcade.app import read_session, session_path
from codex_arcade.stats import atomic_json


def stop(workspace=""):
    current=read_session()
    if not current:return False
    # A stop from another workspace cannot end the visible project's arcade.
    if workspace and current.get("workspace") and workspace != current["workspace"]:return False
    if current.get("status")=="stop":return False
    current["status"]="stop";atomic_json(session_path(),current);return True


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--workspace",default="");args=parser.parse_args();stop(args.workspace)
