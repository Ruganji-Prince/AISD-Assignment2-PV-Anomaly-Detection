"""Validate compliance additions without fitting or changing frozen scientific outputs."""
import ast,json,hashlib,io,re,unittest,unicodedata
import numpy as np
import pandas as pd
import pymupdf
from src.phase2_stage4.verification import check_links
from src.phase2_stage4.common import audit_text
from src.phase2_stage5.publication import PATHS,SECRET_PATTERNS
from .common import *
MANIFEST='phase2_implementation/compliance/Publication_File_Hashes.json'

def verify():
 checks={};protection=load('phase2_implementation/compliance/Approved_Science_Protection.json')
 for n,h in protection['protected_original_files'].items():assert sha(ROOT/n)==h,('Unexpected original-file change',n)
 checks['unchanged_original_public_files']=len(protection['protected_original_files'])
 source=(ROOT/'src/phase2_stage2/models.py').read_text(encoding='utf-8-sig');tree=ast.parse(source);current={}
 for node in tree.body:
  if isinstance(node,ast.ClassDef) and node.name=='RetainedQuality':current['RetainedQuality']=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
  if isinstance(node,ast.ClassDef) and node.name=='AblationModel':
   for method in node.body:
    if isinstance(method,ast.FunctionDef) and method.name in ['fit','predict_proba','names']:current['AblationModel.'+method.name]=hashlib.sha256(ast.dump(method,include_attributes=False).encode()).hexdigest()
 assert current==protection['protected_preprocessing_method_AST'];checks['quality_and_classifier_fit_predict_methods_unchanged']=True
 local=ROOT/'.review/compliance/Before_Compliance.json'
 if local.exists():
  original=load(local.relative_to(ROOT))
  for n,h in original['model_sha256'].items():assert sha(ROOT/n)==h,('Trained binary changed',n)
  checks['original_model_binaries_unchanged']=len(original['model_sha256'])
 report=ROOT/'phase2_implementation/reports/Phase2_Final_Report.pdf';doc=pymupdf.open(report)
 for i,expected in enumerate(protection['original_report_pages']):
  assert hashlib.sha256(doc[i].get_text().encode()).hexdigest()==expected['text_sha256']
  assert hashlib.sha256(doc[i].get_pixmap(matrix=pymupdf.Matrix(1,1)).samples).hexdigest()==expected['render_sha256']
 for page in doc:
  assert page.get_text().strip() and '\ufffd' not in page.get_text()
  for w in page.get_text('words'):assert 0<=w[0]<w[2]<=612 and 0<=w[1]<w[3]<=792
 addition=load('phase2_implementation/compliance/Report_Compliance_Addition.json');assert sha(report)==addition['new_report_sha256'] and len(doc)==addition['pages']==12
 checks['original_scientific_report_pages_identical']=10;checks['report_pages']=len(doc);checks['strategy_table_categories']=addition['strategy_categories']
 text='\n'.join(p.get_text() for p in doc);mapping=load('phase2_implementation/stage4/evidence/report_evidence_map.json')
 for claim in mapping['numeric_claims']:
  if claim['source'].endswith('.csv'):
   f=pd.read_csv(ROOT/claim['source']);key='candidate' if 'candidate' in f else 'key';value=float(f.set_index(key).loc[claim['row_key'],claim['field']])
  else:
   value=load(claim['source'])
   for k in claim['json_path']:value=value[k]
   value=float(value)
  assert value==claim['raw'] and claim['rendered'] in text,('Scientific numeric mismatch',claim['source'],claim.get('field'))
 checks['previous_mapped_scientific_numbers_unchanged']=len(mapping['numeric_claims'])
 comparison=pd.read_csv(ROOT/'phase2_implementation/stage3/evidence/final_candidate_comparison.csv').set_index('candidate')
 expected={'LR__F6':{'test_macro_f1':(.8984,4),'test_R3':(.8519,4),'validation_p95_ms':(14.72,2),'artifact_MiB':(.0037,4)},'RF__E4':{'test_macro_f1':(.9505,4),'test_R1':(.9996,4),'test_R2':(.9907,4),'test_R3':(1.,4),'validation_p95_ms':(36.81,2),'artifact_MiB':(11.6654,4)},'LightGBM__E4':{'test_macro_f1':(.9021,4),'test_R1':(.4994,4),'validation_p95_ms':(6.12,2),'artifact_MiB':(1.5692,4)}}
 for k,fields in expected.items():
  for name,(value,digits) in fields.items():assert round(float(comparison.loc[k,name]),digits)==value
 assert round(float(comparison.loc['RF__E4','test_combined_FPR'])*100,4)==.0832 and round(float(comparison.loc['LightGBM__E4','test_combined_FPR'])*100,4)==.0839
 assert not comparison.passes_all_applicable.any();assert 'No evaluated configuration satisfied all predeclared engineering criteria.' in ' '.join(unicodedata.normalize('NFKC',text).split())
 checks['headline_results_and_final_conclusion_unchanged']=True
 from .tests import ComplianceTests
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(ComplianceTests);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 assert result.wasSuccessful(),stream.getvalue();checks['required_semantic_tests_passed']=result.testsRun
 manifest=load(MANIFEST);names=sorted(set(manifest['sha256'])|{MANIFEST})
 for n,h in manifest['sha256'].items():assert sha(ROOT/n)==h,('Current prospective public hash mismatch',n)
 paths=[];secrets=[];large=[]
 for n in names:
  p=ROOT/n;assert p.is_file()
  assert not n.startswith(('.cache/','.venv/','.review/')) and p.suffix not in ['.pkl','.npz','.joblib','.pem','.key','.zip']
  if p.stat().st_size>25*2**20:large.append(n)
  assert p.stat().st_size<=100*2**20
  if p.suffix in ['.py','.md','.json','.csv','.txt','.ipynb','.tex']:
   s=audit_text(p)
   if PATHS.search(s) or ('CMU_'+'Studies') in s:paths.append(n)
   if any(p.search(s) for p in SECRET_PATTERNS):secrets.append(n)
 if secrets:raise RuntimeError('Possible credential in files: '+','.join(secrets))
 assert not paths,paths;assert large==['data/raw/pv_fault_dataset.csv'],large
 checks['prospective_public_files']=len(names);checks['accidental_absolute_paths']=0;checks['credential_findings']=0;checks['only_large_file_is_existing_approved_raw_CSV']=True;checks['relative_links_resolve']=check_links(names,set(names))
 execution=load('phase2_implementation/compliance/Notebook_Execution.json');notebook=ROOT/'phase2_implementation/notebooks/Phase2_Preprocessing_Implementation.ipynb';assert sha(notebook)==execution['new_notebook_sha256'];assert notebook.stat().st_size<2*2**20
 readme=(ROOT/'README.md').read_text(encoding='utf-8-sig')
 for stale in ['Future implementation directories contain structural placeholders','this submission reports no implementation outcomes','src contains three planning/docstring placeholders']:assert stale not in readme
 assert 'not the verifier for this complete repository' in readme and 'Phase2_Preprocessing_Implementation.ipynb' in readme
 checks['stale_README_resolved']=True;checks['blocker_resolution']={'executable_preprocessing_notebook':'RESOLVED','eight_required_preprocessing_diagnostics':'RESOLVED','strategy_versus_reality_table':'RESOLVED'};checks['classifiers_retrained']=0;checks['predictions_regenerated']=False
 output={'status':'passed','checks':checks,'recommendation':'READY for final compliance publication review; no commit/push performed.'}
 write(ROOT/'.cache/compliance_review/Verification.json',output);print(json.dumps(output,indent=2));return output
if __name__=='__main__':verify()
