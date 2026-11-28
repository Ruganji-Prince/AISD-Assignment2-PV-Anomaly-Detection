"""Independent source, original-model and scientific-preservation checks; no network."""
import hashlib
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from joblib import parallel_backend
from src.inference.cli import load_model, SHA256

ROOT=Path(__file__).resolve().parents[2]
APPROVED_EXISTING_CHANGES={'web/static/index.html','web/static/app.js','web/static/api.js','web/static/style.css','frontend/build.py','deployment/decoupled/test_frontend.py'}

class ReplayAssetsTests(unittest.TestCase):
    def test_scientific_files_and_original_replay_preserved(self):
        proof=json.loads((ROOT/'technical_evaluation/PV_Replay_Verification.json').read_text())
        for name,expected in proof['protected_sha256'].items():
            if name in APPROVED_EXISTING_CHANGES:continue
            with self.subTest(file=name):self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected)
        self.assertEqual(hashlib.sha256((ROOT/'models/rf_e4/model.pkl').read_bytes()).hexdigest(),SHA256)
        self.assertEqual(hashlib.sha256((ROOT/'web/data/pv_historical_replay.json').read_bytes()).hexdigest(),proof['public_json_sha256'])

    def test_all150_source_values_and_real_original_model_predictions(self):
        proof=json.loads((ROOT/'technical_evaluation/PV_Replay_Verification.json').read_text())
        public=json.loads((ROOT/'web/data/pv_historical_replay.json').read_text())
        raw=pd.read_csv(ROOT/'data/raw/pv_fault_dataset.csv',nrows=1006129,float_precision='round_trip')
        inputs=[]
        for item,record in zip(public['observations'],proof['observations'],strict=True):
            i=record['train_source_row_index'];self.assertTrue(0<=i<1006129)
            self.assertEqual(item['source_class'],int(raw.at[i,'f_nv']))
            self.assertEqual(list(item['measurements']),['vdc1','vdc2','idc1','idc2'])
            self.assertEqual(item['measurements'],{k:float(raw.at[i,k]) for k in item['measurements']})
            inputs.append(item['measurements'])
        with parallel_backend('sequential'):pred=load_model().pipeline.predict_proba(pd.DataFrame(inputs)).argmax(axis=1)
        np.testing.assert_array_equal(pred,[r['rf_e4_predicted_class'] for r in proof['observations']])
        self.assertEqual(sum(r['ground_truth_class']!=r['rf_e4_predicted_class'] for r in proof['observations']),13)

    def test_range_table_matches_all20_verified_statistics(self):
        from html.parser import HTMLParser
        class Cells(HTMLParser):
            def __init__(self):super().__init__();self.inside=False;self.cells=[];self.cell=False
            def handle_starttag(self,tag,attrs):
                if tag=='details' and dict(attrs).get('id')=='observed-ranges':self.inside=True
                if self.inside and tag=='td':self.cell=True
            def handle_endtag(self,tag):
                if tag=='details':self.inside=False
                if tag=='td':self.cell=False
            def handle_data(self,text):
                if self.cell:self.cells.append(text)
        parser=Cells();parser.feed((ROOT/'web/static/index.html').read_text(encoding='utf8'))
        stats=pd.read_csv(ROOT/'technical_evaluation/PV_Class_Measurement_Ranges.csv',float_precision='round_trip')
        self.assertEqual(parser.cells,[f'{r.p05:.4f}–{r.p95:.4f}' for r in stats.itertuples()])

if __name__=='__main__':unittest.main()
