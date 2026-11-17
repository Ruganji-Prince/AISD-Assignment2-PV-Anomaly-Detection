"""Read-only evaluation; never fits, tunes, selects thresholds or overwrites evidence."""
import argparse
import hashlib
import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from src.phase2_stage1.contracts import ROOT, TRAIN, BLOCK13, TRAIN_COUNTS, index_digest, sha
from src.phase2_stage1.evaluation import evaluate
from src.phase2_stage3.common import FrozenPredictor, load_part, TEST, BLOCK14
from src.inference.cli import load_model

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-originals',action='store_true',help='Also requires privately preserved .cache/stage2/models and .cache/stage3 test references')
    args=parser.parse_args()
    proof=json.loads((ROOT/'reports/model_verification.json').read_text())
    assert sha(ROOT/'data/raw/pv_fault_dataset.csv')=='717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a'
    train=load_part(TRAIN); val=load_part(BLOCK13);test=load_part(TEST)
    assert train.f_nv.value_counts().to_dict()==TRAIN_COUNTS
    assert set(train.index).isdisjoint(val.index) and set(train.index).isdisjoint(test.index) and set(val.index).isdisjoint(test.index)
    reference=pd.read_csv(ROOT/'phase2_implementation/stage2/evidence/sensor_ablation_validation.csv').set_index('key')
    keys=list(reference.index) if args.all_originals else ['RF__E4']
    checked=[]
    for key in keys:
        if args.all_originals:
            path=ROOT/'.cache/stage2/models'/f'{key}.pkl'
            expected=proof['original_models'][key]['sha256']
            assert sha(path)==expected, key
            model=pickle.loads(path.read_bytes())
        else:model=load_model()
        assert model.fit_rows_==1006129 and model.fit_index_digest_==index_digest(train.index)
        assert np.array_equal(model.classes_,np.arange(5))
        assert not set(model.channels)&{'f_nv','acquisition_index','source_position','block'}
        pipeline=model.pipeline;clean=pipeline.named_steps['quality'].transform(train[model.channels])
        numeric=pipeline.named_steps['columns'].named_transformers_['numeric']
        np.testing.assert_allclose(numeric.named_steps['median'].statistics_,clean.median(),rtol=1e-12,atol=1e-12)
        if 'scale' in numeric.named_steps:
            np.testing.assert_allclose(numeric.named_steps['scale'].mean_,clean.mean(),rtol=1e-12,atol=1e-12)
            np.testing.assert_allclose(numeric.named_steps['scale'].var_,clean.var(ddof=0),rtol=1e-12,atol=1e-12)
        assert pipeline.named_steps['model'].get_params()==model.frozen_estimator_params
        weights=pipeline.named_steps['model'].class_weight
        assert all(weights[k]==len(train)/(5*TRAIN_COUNTS[k]) for k in range(5))
        assert pipeline.named_steps['model'].random_state==42
        assert pipeline.named_steps['columns'].remainder=='drop'
        result=evaluate(FrozenPredictor(model,BLOCK13).predict_proba(val[model.channels]),val.f_nv)
        for metric in ['macro_f1','weighted_f1','hardware_macro_recall','macro_AP']:
            # Parallel RF summation changes near ties at machine epsilon; observed AP difference ~3.1e-8.
            tolerance=1e-7 if metric=='macro_AP' else 1e-12
            assert abs(result[metric]-reference.loc[key,metric])<tolerance,(key,metric)
        if key in ['LR__F6','RF__E4','LightGBM__E4']:
            p=FrozenPredictor(model,TEST).predict_proba(test[model.channels]); result=evaluate(p,test.f_nv)
            expected=proof['test_reproduction'][key]['metrics']
            for metric in ['macro_f1','weighted_f1','hardware_macro_recall','macro_AP']:
                assert abs(result[metric]-expected[metric])<(1e-7 if metric=='macro_AP' else 1e-12)
            assert result['confusion_matrix']==expected['confusion_matrix']
            if args.all_originals:
                with np.load(ROOT/'.cache/stage3'/f'{key}_test.npz') as original:
                    assert np.array_equal(test.index,original['index']) and np.array_equal(test.f_nv,original['y'])
                    np.testing.assert_allclose(p,original['p'],atol=1e-12,rtol=1e-12,equal_nan=True)
            thresholds=json.loads((ROOT/'phase2_implementation/stage3/evidence/stage3_threshold_selection.json').read_text())['results']
            threshold=thresholds[key]['threshold'];block14=load_part(BLOCK14)
            alert=evaluate(FrozenPredictor(model,BLOCK14).predict_proba(block14[model.channels]),block14.f_nv,threshold)['hardware_alert_metrics']
            for metric in ['TP','FP','FN']:assert alert[metric]==thresholds[key][metric],(key,metric)
        checked.append(key)
    receipt=ROOT/'phase2_implementation/stage3/evidence/threshold_freeze_receipt.json'
    freeze=json.loads(receipt.read_text());access=json.loads((receipt.parent/'test_access_started.json').read_text())
    assert freeze['created_utc']<access['created_utc'] and sha(receipt)==access['receipt_sha256']
    assert sha(receipt.parent/'stage3_threshold_selection.json')==freeze['threshold_sha256']==access['threshold_sha256']
    assert sha(receipt.parent/'stage3_protocol.json')==freeze['protocol_sha256']
    for item in json.loads((receipt.parent/'figure_inventory.json').read_text()):assert sha(ROOT/item['file'])==item['sha256']
    print(json.dumps({'status':'PASS','checked_models':checked,'no_fitting_or_threshold_search':True,'legacy_test_exposure':True,'RF_AP_rank_tie_tolerance':1e-7},indent=2))
if __name__=='__main__':main()
