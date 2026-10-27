"""Verify Stage 2 without fitting or using block 14/test predictions."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.phase2_stage2.verification import verify
if __name__=='__main__':print(json.dumps(verify(),indent=2))
