"""Run only approved Stage 2 validation-channel ablation and resource evaluation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.phase2_stage2.run import main
if __name__=='__main__':main()
