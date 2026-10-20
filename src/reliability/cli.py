import argparse, json
from pathlib import Path
from .data import generate_demo_data
from .model import train_and_evaluate

def main():
    p=argparse.ArgumentParser(prog="reliability"); sub=p.add_subparsers(dest="command",required=True)
    d=sub.add_parser("demo"); d.add_argument("--rows",type=int,default=6000)
    d.add_argument("--output",type=Path,default=Path("artifacts")); a=p.parse_args()
    print(json.dumps(train_and_evaluate(generate_demo_data(a.rows),a.output),indent=2))
if __name__=="__main__": main()
