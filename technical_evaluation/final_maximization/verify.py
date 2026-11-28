"""Read-only release audit. No fitting, cloud changes or historical receipt writes.

Run at the repository root; --live makes bounded public HTTP checks only.
This supplements, and does not relax, historical snapshot verifiers.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FRONT = 'https://pv-anomaly-detection-prince-r-k.vercel.app'
API = 'https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def relative_links():
    failures=[]
    count=0
    for p in ROOT.rglob('*.md'):
        if any(t in p.relative_to(ROOT).parts for t in ['.git','.cache','.review','node_modules','.vercel','__pycache__']):continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf8')):
            target=target.strip('<>').split('#')[0]
            if not target or '://' in target or target.startswith(('mailto:','/')):continue
            count+=1
            # Resolve dot segments before the OS lookup (long Windows clone roots).
            if not (p.parent/target.replace('%20',' ')).resolve().exists():
                failures.append({'file':p.relative_to(ROOT).as_posix(),'target':target})
    return {'relative_links_checked':count,'failures':failures,'scope':'Local file destinations; heading anchors and remote link availability are not certified.'}


def local():
    from src.inference.cli import load_model, predict, SHA256
    from technical_evaluation.common import freeze_check, PARTS, blocks
    freeze_check()
    manifest = load('technical_evaluation/final_maximization/Release_Manifest.json')
    bad = [p for p, h in manifest['protected_sha256'].items() if not (ROOT/p).is_file() or digest(p) != h]
    assert not bad, bad
    d = pd.read_csv(ROOT/'data/raw/pv_fault_dataset.csv', float_precision='round_trip')
    assert d.shape == (1373798, 7)
    assert list(d) == ['vdc1', 'vdc2', 'idc1', 'idc2', 'irr', 'pvt', 'f_nv']
    assert d.isna().sum().sum() == 0 and np.isfinite(d.to_numpy()).all()
    assert int(((d.irr == 0) & (d.pvt == 0)).sum()) == 62
    expected = {'TRAIN': (0, 1006129), 'VALIDATION': (1056990, 1173967), 'TEST': (1227337, 1373798)}
    assert PARTS == expected
    assert len(d)-sum(b-a for a,b in PARTS.values()) == 104231
    leakage = load('technical_evaluation/evidence/rubric2/leakage.json')
    groups = []
    for name, (a,b) in expected.items():
        assert leakage['partitions'][name]['bounds'] == [a,b]
        g = {z['block'] for z in blocks() if a <= z['start'] and z['end_exclusive'] <= b}
        assert g == set(leakage['partitions'][name]['operating_blocks'])
        groups.append(g)
    assert [len(g) for g in groups] == [12,2,2]
    assert all(not groups[i] & groups[j] for i in range(3) for j in range(i))
    for item in leakage['feature_vectors'].values():
        assert all(x['shared_distinct_feature_vectors'] == 0 for x in item['cross_partition_overlap'])
    duplicate_checks=[]
    for features in [list(d)[:6],list(d)[:4]]:
        hashes={name:pd.util.hash_pandas_object(d.iloc[a:b][features],index=False).to_numpy() for name,(a,b) in expected.items()}
        for i,name in enumerate(expected):
            for other in list(expected)[:i]:
                # Zero hash intersection implies no equal vectors. Any collision must fail for manual review.
                shared=np.intersect1d(hashes[name],hashes[other])
                assert len(shared)==0,(features,name,other,len(shared))
                duplicate_checks.append({'physical_channels':len(features),'first':name,'second':other,'shared_hashes':0})
    cal = load('technical_evaluation/refinement/results/calibration/calibration_selection_freeze.json')
    assert not cal['new_calibrated_threshold_search']
    assert all(x['fit_eval_overlap'] == x['source_tile_overlap'] == 0 for x in cal['folds'])
    model = load_model()
    cases = load('deployment/example_cases.json')
    for c in cases:
        assert predict(c['input'], model) == c['output']
    # Independently verify original fitted median statistics against TRAIN.
    train = d.iloc[:1006129][model.channels]
    quality = model.pipeline.named_steps['quality'].transform(train)
    median = model.pipeline.named_steps['columns'].named_transformers_['numeric'].named_steps['median']
    np.testing.assert_allclose(median.statistics_, np.nanmedian(quality,axis=0), rtol=0, atol=1e-12)
    counts=d.iloc[:1006129].f_nv.value_counts().sort_index()
    class_weights=model.pipeline.named_steps['model'].class_weight
    expected_weights={int(k):1006129/(5*int(n)) for k,n in counts.items()}
    for k,v in expected_weights.items():
        assert abs(class_weights[k]-v)<1e-12
    count = 0
    def walk(x):
        nonlocal count
        if isinstance(x, dict):
            if 'confusion_matrix' in x and 'macro_f1_fixed_five' in x:
                cm = np.asarray(x['confusion_matrix'],dtype=float)
                den = cm.sum(1) + cm[:,:5].sum(0)
                f = np.divide(2*np.diag(cm[:,:5]),den,out=np.zeros(5),where=den>0)
                assert abs(f.mean()-x['macro_f1_fixed_five']) < 1e-12
                count += 1
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    for folder in ['technical_evaluation/evidence','technical_evaluation/refinement/results']:
        for p in (ROOT/folder).rglob('*.json'): walk(json.loads(p.read_text(encoding='utf8')))
    linkcheck = relative_links()
    assert not linkcheck['failures'], linkcheck
    return {'status':'PASS','protected_release_files':len(manifest['protected_sha256']),
            'model_sha256':SHA256,'raw_shape':list(d.shape),'missing_and_infinite_N':0,
            'paired_zero_N':62,'split_bounds':expected,'excluded_N':104231,
            'TRAIN_medians_recomputed':median.statistics_.tolist(),'CLI_cases':5,
            'TRAIN_class_support':{int(k):int(v) for k,v in counts.items()},
            'TRAIN_class_weights_recomputed':expected_weights,
            'cross_partition_duplicate_rechecks':duplicate_checks,
            'macro_F1_recomputed_from_saved_confusions':count,'links':linkcheck,
            'scope':'Current raw/schema/exact-feature-overlap/median/CLI/hash/metric checks; full-neighbor, fold fitting and calibration experiments inspected, not refitted here.'}


def request(base,path,method='GET',value=None,headers=None,raw=None):
    data = raw if raw is not None else json.dumps(value).encode() if value is not None else None
    h = dict(headers or {})
    if data is not None: h['Content-Type']='application/json'
    started=time.perf_counter()
    req=urllib.request.Request(base+path,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(req,timeout=120) as r: result=(r.status,r.read(),dict(r.headers))
    except urllib.error.HTTPError as e: result=(e.code,e.read(),dict(e.headers))
    return (*result,(time.perf_counter()-started)*1000)


def live():
    from src.inference.cli import SHA256
    status,body,_,ms=request(API,'/api/health')
    health=json.loads(body)
    assert status == 200 and health['model_sha256'] == SHA256
    assert b'PV Intelligence API' in request(API,'/')[1]
    classes=[]
    for c in load('deployment/example_cases.json'):
        status,body,headers,elapsed=request(API,'/api/predict','POST',c['input'])
        output=json.loads(body)
        assert status==200 and all(output[k]==v for k,v in c['output'].items())
        classes.append({'class':output['predicted_class'],'HTTP':status,'end_to_end_ms':elapsed,
                        'server_timing':next((v for k,v in headers.items() if k.lower()=='server-timing'),None)})
    origins=load('docs/final-release/Live_API_Verification.json')['all_six_origins']
    cors=[]
    for origin in origins+['https://unrelated.invalid']:
        status,_,h,_=request(API,'/api/predict','OPTIONS',headers={'Origin':origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
        h={k.lower():v for k,v in h.items()}
        assert status==(200 if origin in origins else 400)
        assert h.get('access-control-allow-origin')==(origin if origin in origins else None)
        assert 'access-control-allow-credentials' not in h
        cors.append({'origin':origin,'HTTP':status})
    invalid=[]
    for name,value in [('missing',{}),('target',dict(load('deployment/example_cases.json')[0]['input'],f_nv=0)),('negative',dict(load('deployment/example_cases.json')[0]['input'],idc1=-1))]:
        assert request(API,'/api/predict','POST',value)[0]==422
        invalid.append(name)
    for name,raw,code in [('duplicate',b'{"vdc1":1,"vdc1":2}',422),('nonfinite',b'{"idc1":NaN}',422),('oversize',b'x'*2049,413)]:
        assert request(API,'/api/predict','POST',raw=raw)[0]==code
        invalid.append(name)
    assets=[]
    for x in load('docs/final-release/Frontend_Manifest.json')['files']:
        if not x['path'].startswith('static/'):continue
        path='/'+x['path'][7:]
        if path=='/index.html':path='/'
        status,body,_,_=request(FRONT,path,headers={'x-vercel-skip-toolbar':'1'})
        assert status==200 and hashlib.sha256(body).hexdigest()==x['sha256'],path
        assets.append(path)
    return {'status':'PASS','health_HTTP':200,'first_health_network_ms':ms,'five_cases':classes,
            'CORS':cors,'invalid_rejected':invalid,'served_static_asset_hashes_match':assets,
            'scope':'Bounded serving parity checks, not accuracy, load testing, a new latency benchmark or forced cold-start measurement.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--tests',action='store_true')
    args=parser.parse_args()
    result={'local':local()}
    if args.tests:
        commands=[['technical_evaluation.tests','technical_evaluation.refinement.tests'],
                  ['discover','-s','tests'],['discover','-s','web/tests'],
                  ['deployment.azure.test_context','deployment.azure.test_deployment','deployment.decoupled.test_backend','deployment.decoupled.test_frontend']]
        for command in commands:
            subprocess.run([sys.executable,'-B','-m','unittest',*command],cwd=ROOT,check=True)
        result['regression_tests']=50
    if args.live: result['live']=live()
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
