"""Prepare an isolated frozen-source/raw-data workspace; does not fit models."""
from pathlib import Path
import argparse,subprocess,zipfile,io,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
COMMIT='34ab15ed18abb29defc0f30baa284f189fc05aef'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work-dir',type=Path,required=True);p.add_argument('--git',default='git');a=p.parse_args()
work=a.work_dir.resolve();source=work/'source';assert not source.exists(),'Use a new workspace; never overwrite prior reconstruction artifacts.'
assert subprocess.run([a.git,'cat-file','-e',COMMIT+'^{commit}'],cwd=ROOT,capture_output=True).returncode==0,'Fetch the documented source commit before preparation.'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
raw=ROOT/'data/raw/pv_fault_dataset.csv';assert sha(raw)=='717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a'
archive=subprocess.check_output([a.git,'archive','--format=zip',COMMIT,'src','phase1_strategy','phase2_implementation'],cwd=ROOT)
work.mkdir(parents=True,exist_ok=True);source.mkdir();z=zipfile.ZipFile(io.BytesIO(archive));z.extractall(source)
dest=source/'data/raw/pv_fault_dataset.csv';dest.parent.mkdir(parents=True);shutil.copy2(raw,dest);assert sha(dest)==sha(raw)
protected={}
for folder in ['phase1_strategy','src','phase2_implementation/reports','phase2_implementation/model_comparison']:
 for path in (ROOT/folder).rglob('*'):
  if path.is_file() and '__pycache__' not in path.parts:protected[path.relative_to(ROOT).as_posix()]=sha(path)
(work/'Protected_Original_Files.json').write_text(json.dumps(protected,indent=2),encoding='utf8')
(work/'Source_Snapshot.json').write_text(json.dumps({'commit':COMMIT,'source_sha256':{n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith('/')},'raw_sha256':sha(raw)},indent=2),encoding='utf8')
print('Prepared frozen source/data; no model fitting or predictions performed.')
