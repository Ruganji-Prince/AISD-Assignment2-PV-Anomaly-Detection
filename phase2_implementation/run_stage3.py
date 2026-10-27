import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.phase2_stage3.run import freeze,final_test
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('step',choices=['freeze','test']);a=p.parse_args()
 {'freeze':freeze,'test':final_test}[a.step]()
