"""Portable evidence-only verification; scientific experiment files are never rewritten."""
import ast,json,re,sys
import numpy as np
import pandas as pd
import pymupdf
from urllib.parse import unquote
from .common import *
PATH_PATTERN=re.compile(r'(?<![A-Za-z])(?:[A-Za-z]:[\\/]|/(?:Users|home)/)')
E3='phase2_implementation/stage3/evidence/'
def without_fences(s):return re.sub(r'(```|~~~).*?\1','',s,flags=re.S)
def check_links(paths,public=None):
 broken=[];count=0
 for name in paths:
  if not name.endswith(('.md','.ipynb')):continue
  path=ROOT/name
  if name.endswith('.ipynb'):text='\n'.join(''.join(c['source']) for c in load(name)['cells'] if c['cell_type']=='markdown')
  else:text=path.read_text(encoding='utf-8-sig')
  text=without_fences(text)
  for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
   link=link.strip().strip('<>')
   if not link or link.startswith(('#','http:','https:','mailto:')):continue
   link=unquote(link.split('#')[0]);target=(path.parent/link).resolve();count+=1
   if not target.exists():broken.append(name+': '+link)
   elif public is not None and target.relative_to(ROOT).as_posix() not in public:broken.append(name+': non-public target '+link)
 assert not broken,broken
 return count

def verify():
 checks={};manifest=load('phase2_implementation/stage4/evidence/Publication_File_Hashes.json');public=set(manifest['sha256'])|{'phase2_implementation/stage4/evidence/Publication_File_Hashes.json'}
 for name,h in manifest['sha256'].items():assert sha(ROOT/name)==h,name
 checks['public_file_hashes_match']=len(manifest['sha256'])
 baseline=OUT/'Protected_Stage123_Hashes.json'
 if baseline.exists():checks['local_protected_originals_unchanged']=protect()
 comp=pd.read_csv(ROOT/(E3+'final_candidate_comparison.csv')).set_index('candidate');details=load(E3+'final_test_details.json')['results'];threshold=load(E3+'stage3_threshold_selection.json');receipt=load(E3+'threshold_freeze_receipt.json');event=load(E3+'test_access_started.json')
 thash=sha(ROOT/(E3+'stage3_threshold_selection.json'));assert receipt['threshold_sha256']==event['threshold_sha256']==thash;assert threshold['frozen_utc']<=receipt['created_utc']<event['created_utc'];checks['threshold_freeze_precedes_test']=True
 criteria=pd.read_csv(ROOT/(E3+'final_engineering_criteria.csv'),keep_default_na=False)
 for key,r in comp.iterrows():
  m=details[key];cm=np.asarray(m['confusion_matrix']);support=cm.sum(1);assert support.tolist()==[124512,2361,2270,2410,14908];assert cm.shape==(5,6)
  tp=np.diag(cm[:,:5]);precision=np.divide(tp,cm[:,:5].sum(0),out=np.zeros(5,dtype=float),where=cm[:,:5].sum(0)>0);recall=tp/support;f1=np.divide(2*precision*recall,precision+recall,out=np.zeros(5,dtype=float),where=precision+recall>0)
  assert abs(f1.mean()-r.test_macro_f1)<1e-12 and abs(np.average(f1,weights=support)-r.test_weighted_f1)<1e-12
  for k in range(5):
   for name,val in [('precision',precision[k]),('recall',recall[k]),('f1',f1[k]),('support',support[k])]:assert abs(val-m['per_class'][str(k)][name])<1e-12
  assert abs(np.mean([m['per_class'][str(k)]['AP'] for k in range(5)])-r.test_macro_AP)<1e-12
  if key!='LR__F6':assert abs(details[key.split('__')[0]+'__F6']['macro_f1']-m['macro_f1']-r.same_family_test_delta_s)<1e-12
  flags=[r.test_macro_f1>=.8,min(recall[1:4])>=.9,None if key=='LR__F6' else r.same_family_test_delta_s<=.05,None if key=='LR__F6' else r.physical_channels<=4,r.test_combined_FPR<=.01,r.validation_p95_ms<=10,r.artifact_MiB<=10,r.validation_dropout_loss<=.05]
  names=['macro_f1_ge_080','each_hardware_classification_recall_ge_090','same_family_test_delta_le_005','sparse_channels_le_4','test_combined_alert_FPR_le_001','validation_p95_le_10ms','artifact_le_10MiB','validation_dropout_loss_le_005']
  expected={n:('N/A' if f is None else ('PASS' if f else 'FAIL')) for n,f in zip(names,flags)};assert criteria[criteria.candidate==key].set_index('criterion').status.to_dict()==expected
  assert bool(r.passes_all_applicable)==all(f for f in flags if f is not None)
 assert not comp.passes_all_applicable.any();checks['confusion_derived_classification_and_engineering_criteria_match']=True
 weights=load('phase2_implementation/stage1/evidence/class_weights.json');assert weights['training_rows']==1006129
 for k,n in weights['training_counts'].items():assert weights['weights'][k]==1006129/(5*n)
 models=load('phase2_implementation/stage4/evidence/final_model_specifications.json')['candidates'];resource=load('phase2_implementation/stage4/evidence/resource_protocol_public.json')['candidates']
 for key in models:
  m=models[key];assert m['class_weights']==weights['weights'];assert m['fit_rows']==1006129;assert not any(x in n.lower() for n in m['feature_names'] for x in ['timestamp','source_position','acquisition_index','block_id'])
  expected=['vdc1','vdc2','idc1','idc2','irr','pvt'] if key=='LR__F6' else ['vdc1','vdc2','idc1','idc2'];assert m['raw_channels']==expected
  r=resource[key];samples=r['latency']['latency_samples_ms'];assert len(samples)==2000 and r['latency']['warmups']==100;assert abs(np.percentile(samples,95)-comp.loc[key,'validation_p95_ms'])<1e-10
  source=ROOT/m['source']
  if source.exists():
   assert sha(source)==m['source_sha256']==r['source_sha256'];original=load(m['source']);assert m['estimator_parameters']==original['details']['estimator_parameters'];assert r['latency']=={n:v for n,v in original['details']['latency'].items() if n!='threadpools'}
 checks['training_weights_features_parameters_and_resource_projections_match']=True
 audit=load('phase2_implementation/stage4/evidence/report_evidence_map.json');report=REPORTS/'Phase2_Final_Report.pdf';source=REPORTS/'Phase2_Final_Report.md';assert sha(report)==audit['report_sha256'] and sha(source)==audit['source_sha256']
 text=source.read_text(encoding='utf8');doc=pymupdf.open(report);pdftext='\n'.join(page.get_text() for page in doc)
 for claim in audit['numeric_claims']:
  if claim['source'].endswith('.csv'):
   frame=pd.read_csv(ROOT/claim['source']);index='candidate' if 'candidate' in frame else 'key';value=float(frame.set_index(index).loc[claim['row_key'],claim['field']])
  else:
   value=load(claim['source'])
   for k in claim['json_path']:value=value[k]
   value=float(value)
  assert value==claim['raw'];s=f"{value*claim['multiplier']:.{claim['digits']}f}";assert s==claim['rendered'] and s in text and s in pdftext
 assert len(doc)==audit['pages']==10;assert all(x['scale']==1 and x['spare_height_pt']>=0 for x in audit['layout'])
 for figure in audit['figures']:
  assert sha(ROOT/figure['source'])==figure['sha256'];assert any(x in figure['caption'] for x in ['TRAIN','VALIDATION','TEST'])
 assert len(audit['figures'])==7 and len(audit['tables'])==8
 table8=next(x for x in audit['tables'] if x['number']==8)
 assert [[r[1],r[2],r[3]] for r in table8['rows']]==[[criteria[criteria.criterion==name].set_index('candidate').loc[k,'status'] for k in ['LR__F6','RF__E4','LightGBM__E4']] for name in names]
 checks['report_numbers_match_evidence']=len(audit['numeric_claims']);checks['report_pages']=len(doc);checks['selected_figures_correct_populations']=7;checks['report_tables']=8
 assert 'No evaluated configuration satisfied all predeclared engineering criteria.' in text
 for phrase in ['not pristine or previously unseen','not verified days, sessions or hours','not causal','seven predeclared']:
  assert phrase.lower() in text.lower(),phrase
 assert not re.search(r'\b(I|me|my|mine|we|us|our|ours|you|your|yours)\b',text,flags=re.I)
 assert not any(s in text for s in ['Codex','Stage 1 prompt','Stage 2 prompt','the AI generated'])
 assert 'not established as globally minimum sensing' in text and 'project aspirations' in text
 checks['limitations_scope_and_neutral_report_style']=True
 distribution=pd.read_csv(ROOT/'phase1_strategy/Class_Distribution.csv');split=load('phase1_strategy/Phase1_Split_Manifest.json');discrepancy=load('phase2_implementation/stage1/evidence/row_count_discrepancy.json')
 assert int(distribution.N.sum())==split['raw_N']==1373798 and split['raw_total_columns']==7 and len(split['operating_blocks'])==16
 for value in distribution.N:assert f'{int(value):,}' in text
 assert discrepancy['thresholds']['irr_ge_100']['N']==515958 and discrepancy['thresholds']['irr_ge_100']['class_counts']==discrepancy['paper_class_counts']
 for value in weights['weights'].values():assert f'{value:.6f}' in text
 assert '[0,1006129)' in text and '[1056990,1089790)' in text and '[1140571,1173967)' in text and '[1227337,1373798)' in text
 shap=pd.read_csv(ROOT/(E3+'shap_mean_absolute.csv'));assert shap[shap.feature.str.startswith('missing__')].mean_abs_SHAP.eq(0).all()
 checks['report_dataset_counts_weights_splits_and_SHAP_caption_match']=True
 path_hits=[];large=[]
 for name in public:
  path=ROOT/name
  if path.stat().st_size>100*2**20:large.append(name)
  if path.suffix.lower() in ['.md','.py','.txt','.csv','.json','.ipynb']:
   s=path.read_text(encoding='utf-8-sig')
   if PATH_PATTERN.search(audit_text(path)):path_hits.append(name)
   assert not re.search(r'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}',s),name
 assert not path_hits,path_hits;assert not large,large;checks['public_absolute_paths_or_obvious_credentials']=0;checks['public_files_over_100MiB']=0
 checks['public_relative_Markdown_links']=check_links(sorted(public),public)
 nb=load('phase2_implementation/notebooks/Phase2_Evidence_Review.ipynb');codes=[x for x in nb['cells'] if x['cell_type']=='code'];assert len(codes)==7
 for cell in codes:
  assert cell['execution_count'] and all(o['output_type']!='error' for o in cell['outputs'])
  for node in ast.walk(ast.parse(''.join(cell['source']))):
   assert not (isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ['fit','fit_transform','partial_fit'])
 checks['executed_evidence_only_notebook_cells']=len(codes)
 raw=ROOT/'data/raw/pv_fault_dataset.csv';assert sha(raw)=='717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a';assert sha(ROOT/'phase1_strategy/Phase1_Strategy_Report.pdf')=='dfb3f253f3e059ece168d9c6edffc10f68a0a21ba8b738a6fb2b2d2c1d962497'
 checks['raw_CSV_and_approved_Phase1_PDF_byte_identical']=True
 target=ROOT/'.cache/stage4/submission_verification.json';write(target,{'status':'passed','checks':checks,'scope':'Evidence-only; no training or prediction; AP protected/checked against authoritative evidence, not recomputed from absent ranking arrays.'});print(json.dumps({'status':'passed','checks':checks},indent=2));return checks
if __name__=='__main__':verify()
