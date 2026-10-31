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
 # Assignment 3 evidence is read only: no estimator fits or notebook execution.
 import numpy as np
 import pandas as pd
 import pymupdf
 report=ROOT/'phase2_implementation/reports/Assignment3_Phase2.pdf'
 meta=load('phase2_implementation/reports/Report_Verification.json')
 assert sha(report)==meta['sha256']
 assert sha(report.with_suffix('.tex'))==meta['source_sha256']
 assert meta['document_class']=='IEEEtran' and meta['mode']=='conference'
 assert sha(report.parent/'IEEEtran.cls')==meta['class_sha256']==load('phase2_implementation/reports/IEEE_Template_Provenance.json')['class_sha256']
 source=report.with_suffix('.tex').read_text(encoding='utf8')
 assert r'\documentclass[conference]{IEEEtran}' in source
 labels=re.findall(r'\\label\{fig:([^}]+)\}',source)
 assert len(labels)==8 and all(r'\ref{fig:'+label+'}' in source for label in labels)
 with pymupdf.open(report) as doc:
  assert len(doc)==meta['pages'] and sum(len(p.get_images()) for p in doc)==8
  assert '??' not in ''.join(p.get_text() for p in doc)
 E=ROOT/'phase2_implementation/compliance'
 dims=pd.read_csv(E/'Pipeline_Stage_Dimensions.csv');assert len(dims)==9
 expected_N={'TRAIN':1006129,'VALIDATION':116977,'TEST':146461}
 expected_P={'six_standard':12,'electrical_native':8,'electrical_derived':13}
 for _,row in dims.iterrows():
  assert row.input_N==expected_N[row.partition] and row.original_predictors==6
  assert row.final_design_P==expected_P[row.policy]
  assert row.post_quality_P==row.post_median_numeric_P==row.retained_physical_channels
  assert row.post_feature_numeric_P+row.indicator_P==row.final_design_P
  assert row.final_design_NxP==f'{row.input_N} x {row.final_design_P}'
 dist=pd.read_csv(E/'Training_Distribution_Diagnostics.csv').set_index('sensor')
 old=pd.read_csv(ROOT/'phase1_strategy/Training_Distributions.csv').set_index('sensor')
 for a,b in [('q1','q1'),('q3','q3'),('skewness','skewness'),('lower_fence','iqr_lower'),('upper_fence','iqr_upper')]:assert np.allclose(dist[a],old[b],rtol=0,atol=1e-10)
 assert (dist.flagged_count==0).all() and (dist.flagged_pct==0).all()
 audit=load('phase2_implementation/compliance/Empirical_Audit.json')
 assert audit['population']=='TRAIN' and audit['N']==1006129 and audit['heldout_fit_guard_passed']
 old_vif=load('phase1_strategy/primary_audit.json')['training_vif']
 assert np.allclose(list(audit['verified_VIF'].values()),list(old_vif.values()),rtol=0,atol=1e-8)
 pca=pd.read_csv(E/'PCA_Diagnostics.csv')
 ref=load('phase2_implementation/compliance/Preprocessing_Reference.json')
 assert np.allclose(pca.explained_variance_ratio,ref['PCA']['explained_variance_ratio'],rtol=0,atol=1e-10)
 assert abs(pca.cumulative_explained_variance.iloc[1]-.9516766680256425)<1e-10
 from PIL import Image
 for record in figs:
  assert record['file'].startswith('figures/')
  with Image.open(ROOT/record['file']) as im:
   assert all(round(v)>=300 for v in im.info['dpi']);im.verify()
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
 print(json.dumps({'status':'PASS','executed_cells':13,'errors':0,'diagnostics':8,'diagnostic_DPI':300,'relative_links':links,'downstream_directories_absent':True,'IEEEtran_conference_report':True,'report_pages':meta['pages'],'measured_partition_policy_stage_rows':len(dims),'TRAIN_statistical_reference_consistency':True,'figure_cross_references':len(labels)},indent=2))
if __name__=='__main__':main()
