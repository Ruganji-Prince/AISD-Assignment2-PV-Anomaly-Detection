"""Read-only checks of the finalized Phase 1 submission; never fits models or rewrites evidence."""
from pathlib import Path
import json,csv,hashlib,re,ast,argparse
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'phase1_strategy'
EXPECTED={0:1162931,1:5999,2:10371,3:6024,4:188473}
SENSORS=['vdc1','vdc2','idc1','idc2','irr','pvt']
PDF_SHA='dfb3f253f3e059ece168d9c6edffc10f68a0a21ba8b738a6fb2b2d2c1d962497'
IGNORED_PARTS={'.git','.venv','.cache','.tools','.review','.uv-cache','.python','__pycache__','.ipynb_checkpoints'}
def submission_file(path):
    return path.is_file() and not (set(path.relative_to(ROOT).parts)&IGNORED_PARTS) and not path.is_relative_to(ROOT/'data/raw/candidate_evidence')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    import pymupdf
    import pandas as pd
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-summary',action='store_true',help='Write verification metadata only; scientific evidence stays unchanged.')
    args=parser.parse_args()
    audit=json.loads((OUT/'primary_audit.json').read_text())
    split=json.loads((OUT/'Phase1_Split_Manifest.json').read_text())
    assert audit['raw_N']==1373798 and audit['raw_total_columns']==7 and audit['raw_predictors']==6
    assert {int(k):v for k,v in audit['class_counts'].items()}==EXPECTED
    assert audit['raw_cells']==9616586 and audit['raw_missing_cells']==0 and audit['raw_missing_pct']==0
    assert audit['raw_complete_rows']==1373798 and audit['raw_incomplete_rows']==0
    assert audit['paired_zero_rows']==62 and [x['length'] for x in audit['paired_zero_runs']]==[1,32,29]
    assert len(split['operating_blocks'])==16 and split['group_rule']==audit['group_rule']
    assert split['group_rule']['allocation_blocks']==[12,2,2] and split['excluded_separator_rows']==104231
    assert split['proposed_split']==audit['proposed_split']
    assert [split['proposed_split'][k]['N'] for k in ['training','validation','test']]==[1006129,116977,146461]
    assert sum(x['N'] for x in split['proposed_split'].values())+104231==1373798
    assert [split['validation_subblocks'][k]['N'] for k in ['model_selection','alert_threshold']]==[32800,33396]
    for name,record in split['proposed_split'].items():
        assert record['end_exclusive']-record['start']==record['N']
        assert sum(record['labels'].values())==record['N'] and min(record['labels'].values())>0
    assert len(audit['training_correlated_pairs'])==5 and all(abs(x['pearson_r'])>=.85 for x in audit['training_correlated_pairs'])
    assert sum(v>10 for v in audit['training_vif'].values())==5
    with (OUT/'Variable_Inventory.csv').open(encoding='utf-8',newline='') as f:inventory=list(csv.DictReader(f))
    assert [r['name'] for r in inventory]==SENSORS+['f_nv']
    assert all(r['loaded_dtype']=='float64' and r['analytical_category']=='Continuous' for r in inventory[:6])
    assert inventory[-1]['loaded_dtype']=='uint8' and inventory[-1]['analytical_category']=='Nominal categorical'
    assert all(int(r['missing_count'])==0 and float(r['missing_pct'])==0 for r in inventory)
    with (OUT/'Class_Distribution.csv').open(encoding='utf-8',newline='') as f:
        assert {int(r['label']):int(r['N']) for r in csv.DictReader(f)}==EXPECTED
    with (OUT/'Training_Distributions.csv').open(encoding='utf-8',newline='') as f:
        stats=list(csv.DictReader(f))
    assert len(stats)==6 and all(int(r['iqr_flagged_count'])==0 and int(r['z_gt_3_count'])==0 for r in stats)
    source=json.loads((OUT/'primary_source_manifest.json').read_text())
    assert len(source)==4 and all(r['commit']=='e9ed8ad8072dcb3ffc643b0f3604219798708551' for r in source)
    assert sha(OUT/'Phase1_Strategy_Report.pdf')==PDF_SHA
    with pymupdf.open(OUT/'Phase1_Strategy_Report.pdf') as pdf:
        text='\n'.join(p.get_text() for p in pdf)
        compact=re.sub(r'[\s,]','',text)
        assert len(pdf)==10 and all(str(n) in compact for n in [1373798,1162931,5999,10371,6024,188473,1006129,116977,146461,104231])
        for word in ['MCAR','MAR','MNAR','Mutual','VIF','StandardScaler','PCA','acquisition_index']:
            assert word in text,word
        overflow=[]
        for i,p in enumerate(pdf):
            for b in p.get_text('blocks',clip=pymupdf.Rect(-100,-100,2000,2000)):
                if b[2]>p.rect.width+1:overflow.append({'page':i+1,'note':'Existing approved content extends past right page boundary; PDF retained unchanged.'})
    assert all((ROOT/p).is_dir() for p in ['data/raw','data/processed','phase1_strategy','phase2_implementation/notebooks','src','figures'])
    for folder in ['data/processed','phase2_implementation','figures']:
        assert not [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='.gitkeep'],folder
    assert not (ROOT/'results').exists() and not (ROOT/'notebooks').exists()
    for name in ['__init__.py','transformers.py','pipeline_builder.py']:
        nodes=ast.parse((ROOT/'src'/name).read_text()).body
        assert len(nodes)==1 and isinstance(nodes[0],ast.Expr) and isinstance(nodes[0].value,ast.Constant) and isinstance(nodes[0].value.value,str)
    guide=(OUT/'Decision_Rationale_Guide.md').read_text(encoding='utf-8')
    assert '## Phase 2 execution appendix' not in guide
    assert guide.count('**Simple explanation:**')==15
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    assert 'Task Type: Multiclass Classification' in readme
    assert not any(p.suffix in {'.ipynb','.joblib','.npz','.png'} for p in ROOT.rglob('*') if submission_file(p))
    counts={k:0 for k in EXPECTED};rows=0;paired=0;neg_irr=0;neg_temp=0
    raw=ROOT/'data/raw/pv_fault_dataset.csv'
    assert sha(raw)=='717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a'
    for chunk in pd.read_csv(raw,chunksize=100000,float_precision='round_trip'):
        assert list(chunk.columns)==SENSORS+['f_nv'] and not chunk.isna().any().any()
        rows+=len(chunk);paired+=int(((chunk.irr==0)&(chunk.pvt==0)).sum())
        neg_irr+=int((chunk.irr<0).sum());neg_temp+=int((chunk.pvt<0).sum())
        for k,v in chunk.f_nv.value_counts().items():counts[int(k)]+=int(v)
    assert rows==1373798 and counts==EXPECTED and paired==62 and neg_irr==1 and neg_temp==24172
    broken=[];paths=[];secrets=[];large=[]
    token_patterns=[r'\bgh[pousr]_[A-Za-z0-9]{30,}\b',r'\bgithub_pat_[A-Za-z0-9_]{40,}\b',r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'https?://[^\s/@:]+:[^\s/@]+@']
    for path in ROOT.rglob('*'):
        if not submission_file(path):continue
        relative=path.relative_to(ROOT).as_posix()
        if path.stat().st_size>50*1024**2:large.append({'file':relative,'bytes':path.stat().st_size})
        if path==raw:continue  # Full numeric schema, counts and hash were validated above.
        if path.suffix=='.pdf':
            with pymupdf.open(path) as doc:content='\n'.join(p.get_text() for p in doc)
        else:content=path.read_text(encoding='utf-8',errors='replace')
        if re.search(r'(?<![A-Za-z])[A-Za-z]:(?:/|\\+)',content):paths.append(relative)
        for pattern in token_patterns:
            if re.search(pattern,content):secrets.append(relative)
        if path.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',content):
                if '://' in target or target.startswith('#'):continue
                target=target.strip('<>').split('#',1)[0]
                if target and not (path.parent/target).exists():broken.append({'file':relative,'target':target})
    assert not secrets and not paths and not broken
    assert [r['file'] for r in large]==['data/raw/pv_fault_dataset.csv']
    result={'status':'passed','official_report_sha256':PDF_SHA,'official_report_pages':10,
            'raw_N':rows,'raw_total_P':7,'predictors':6,'class_counts':counts,'raw_missing_cells':0,
            'paired_zero_positions':paired,'small_negative_irradiance_positions':neg_irr,'negative_temperature_positions':neg_temp,
            'split_N':[1006129,116977,146461],'separator_positions':104231,'blocks':[12,2,2],
            'phase2_results_and_implementation_absent':True,'src_docstring_placeholders_only':True,
            'secret_pattern_matches':secrets,'absolute_Windows_paths':paths,'broken_relative_links':broken,
            'intentional_large_files':large,'approved_PDF_layout_observations':overflow,
            'no_training_or_scientific_report_regeneration':True,'GitHub_push':'not performed'}
    if args.write_summary:(OUT/'Submission_Verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

