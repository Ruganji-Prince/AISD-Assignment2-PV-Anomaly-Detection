from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'phase2_implementation/stage4'
REPORTS=ROOT/'phase2_implementation/reports'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def write(path,obj):
 path.parent.mkdir(exist_ok=True,parents=True);path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')
def audit_text(path):
 path=Path(path);text=path.read_text(encoding='utf-8-sig')
 if path.suffix.lower()=='.py':
  import ast,io,tokenize
  values=[n.value for n in ast.walk(ast.parse(text)) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
  values.extend(t.string for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type==tokenize.COMMENT)
  return '\n'.join(values)
 if path.suffix.lower() not in ['.json','.ipynb']:return text
 def strings(value):
  if isinstance(value,str):yield value
  elif isinstance(value,dict):
   for k,v in value.items():yield str(k);yield from strings(v)
  elif isinstance(value,list):
   for v in value:yield from strings(v)
 return '\n'.join(strings(json.loads(text)))
def protect():
 baseline=OUT/'Protected_Stage123_Hashes.json'
 if baseline.exists():entries=load(baseline.relative_to(ROOT))['sha256']
 else:
  public=load('phase2_implementation/stage4/evidence/Publication_File_Hashes.json')['sha256']
  prefixes=('phase1_strategy/','data/','figures/','src/phase2_stage1/','src/phase2_stage2/','src/phase2_stage3/','phase2_implementation/stage1/','phase2_implementation/stage2/','phase2_implementation/stage3/')
  entries={n:h for n,h in public.items() if n.startswith(prefixes) or n in ['README.md','.gitignore','.gitattributes','requirements.txt','requirements-lock.txt']}
 for name,h in entries.items():
  if sha(ROOT/name)!=h:raise AssertionError('Protected file changed: '+name)
 return len(entries)
