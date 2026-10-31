"""Read-only current-stage verification (does not execute the notebook)."""
from pathlib import Path
import sys,json,hashlib,re,urllib.parse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.preprocessing.common import sha,load
def main():
 p=ROOT/'phase2_implementation/notebooks/Phase2_Preprocessing_Implementation.ipynb';n=json.loads(p.read_text());cs=[c for c in n['cells'] if c['cell_type']=='code']
 assert len(cs)==13 and all(c['execution_count'] is not None for c in cs)
 assert not any(o.get('output_type')=='error' for c in cs for o in c['outputs'])
 assert sha(p)==load('phase2_implementation/compliance/Notebook_Execution.json')['notebook_sha256']
 figs=load('phase2_implementation/compliance/Diagnostic_Inventory.json');assert len(figs)==8
 for x in figs:assert sha(ROOT/x['file'])==x['sha256']
 assert sha(ROOT/'data/raw/pv_fault_dataset.csv')=='717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a'
 assert sha(ROOT/'phase1_strategy/Phase1_Strategy_Report.pdf')=='dfb3f253f3e059ece168d9c6edffc10f68a0a21ba8b738a6fb2b2d2c1d962497'
 forbidden=['noise_robustness','model_comparison','stage1','stage2','stage3','stage4','stage5']
 assert not any((ROOT/'phase2_implementation'/s).exists() for s in forbidden)
 links=0
 for f in ROOT.rglob('*'):
  if not f.is_file():continue
  assert f.suffix not in ['.pkl','.npz','.joblib','.pyc','.pem','.key']
  assert f.stat().st_size<100*2**20
  if f.suffix in ['.md','.ipynb']:
   text=f.read_text(encoding='utf-8-sig')
   if f.suffix=='.ipynb':text='\n'.join(''.join(c['source']) for c in json.loads(text)['cells'])
   for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
    target=target.strip('<>').split('#')[0]
    if not target or '://' in target:continue
    assert (f.parent/urllib.parse.unquote(target)).resolve().exists(),(str(f),target)
    links+=1
 print(json.dumps({'status':'PASS','executed_cells':13,'errors':0,'diagnostics':8,'relative_links':links,'downstream_directories_absent':True},indent=2))
if __name__=='__main__':main()
