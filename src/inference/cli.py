"""Local four-channel inference; no fitting, target input or calibrated confidence."""
import argparse
import hashlib
import json
import math
import pickle
import sys
from pathlib import Path
from importlib.metadata import version
ROOT = Path(__file__).resolve().parents[2]
CHANNELS = ('vdc1', 'vdc2', 'idc1', 'idc2')
LABELS = ('normal', 'short circuit', 'resistive degradation', 'open circuit', 'natural building shade')
MODEL = ROOT / 'models/rf_e4/model.pkl'
SHA256 = '55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb'
VERSIONS = {'numpy': '2.5.4', 'pandas': '3.0.6', 'scipy': '1.18.1', 'scikit-learn': '1.9.1'}
RANGES = {'vdc1': (.3799,363.974), 'vdc2': (.3164,368.749), 'idc1': (.0418,9.6549), 'idc2': (.0046,9.4987)}
def validate(record):
    if not isinstance(record, dict) or set(record) != set(CHANNELS):
        raise ValueError('Exactly vdc1, vdc2 (V), idc1, idc2 (A) required; no target/index/metadata.')
    values = []
    for key in CHANNELS:
        value = record[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f'{key} must be a finite real number.')
        try:
            value = float(value)
        except OverflowError as exc:
            raise ValueError(f'{key} exceeds finite numeric range.') from exc
        if not math.isfinite(value) or value < 0:
            raise ValueError(f'{key} must be finite and nonnegative.')
        values.append(value)
    return values

def load_model(path=MODEL):
    # Vercel build/runtime patches are parity-verified; training used 3.14.7.
    if sys.version_info[:3] not in {(3,14,7), (3,14,8), (3,14,10)}:
        raise RuntimeError('Verified runtimes: Python 3.14.7, 3.14.8 and 3.14.10; use deployment/requirements.txt.')
    for package, expected in VERSIONS.items():
        if version(package) != expected:
            raise RuntimeError(f'{package}=={expected} required for the preserved pickle.')
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('Model integrity mismatch; refusing to unpickle.')
    # Only the pinned, repository-supplied artifact is trusted. Never load user pickles.
    model = pickle.loads(data)
    if model.channels != list(CHANNELS) or list(model.classes_) != list(range(5)):
        raise ValueError('Model schema/class order mismatch.')
    return model

def predict(record, model=None):
    import numpy as np
    import pandas as pd
    values = validate(record)
    model = load_model() if model is None else model
    frame = pd.DataFrame([values], columns=CHANNELS)
    # Same fitted quality/median/indicator/forest pipeline; no fit or target required.
    probabilities = model.pipeline.predict_proba(frame)
    if probabilities.shape != (1,5) or not np.isfinite(probabilities).all():
        raise ValueError('Invalid model output.')
    label = int(probabilities[0].argmax())
    return {'predicted_class': label, 'label': LABELS[label],
            'hardware_fault_class': label in (1,2,3),
            'environmental_shade': label == 4,
            'model_version': 'archived-RF__E4-cf5d0ac4', 'model_sha256': SHA256,
            'range_warnings': [key for key,value in zip(CHANNELS,values)
                               if not RANGES[key][0] <= value <= RANGES[key][1]]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='JSON object with four physical measurements')
    args = parser.parse_args()
    try:
        result = predict(json.loads(args.input.read_text(encoding='utf8')))
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f'Inference error: {exc}\n')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
