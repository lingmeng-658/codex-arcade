import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

from codex_arcade.app import read_session, session_path
from codex_arcade.stats import atomic_json, local_dir


def valid_pid(pid):
    if not isinstance(pid,int) or pid<=0:return False
    if os.name=="nt":
        import ctypes
        handle=ctypes.windll.kernel32.OpenProcess(0x1000,False,pid)
        if handle:ctypes.windll.kernel32.CloseHandle(handle);return True
        return False
    try:os.kill(pid,0);return True
    except OSError:return False


def start(workspace=""):
    path=session_path();path.parent.mkdir(parents=True,exist_ok=True); current=read_session()
    if current.get("status") in ("waiting","running") and valid_pid(current.get("pid")): return False
    if path.exists():
        try:path.unlink()
        except OSError:return False
    token=uuid.uuid4().hex; atomic_json(path,{"token":token,"workspace":workspace,"status":"waiting","pid":os.getpid(),"created":time.time()})
    time.sleep(2.0)
    current=read_session()
    if current.get("token")!=token or current.get("status")!="waiting":return False
    current["status"]="running";current["pid"]=0;atomic_json(path,current)
    flags=0x08000000 if os.name=="nt" else 0
    subprocess.Popen([sys.executable,"-m","codex_arcade","--token",token,"--workspace",workspace],cwd=Path(__file__).parent,creationflags=flags)
    return True


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--workspace",default="");args=parser.parse_args();start(args.workspace)
