import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.phase2_stage5.publication import verify
if __name__=='__main__':verify()
