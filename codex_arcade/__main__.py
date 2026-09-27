import argparse
from .app import launch

parser=argparse.ArgumentParser();parser.add_argument("--token");parser.add_argument("--workspace",default="")
args=parser.parse_args();launch(args.token,args.workspace)
