# Local inference prototype

Status: locally executable prototype using the original, hash-verified RF E4 fitted pipeline. No cloud deployment, real-time guarantee, production monitoring or calibrated reliability is demonstrated. Validation selected RF E4 under four sensing/performance criteria; its archived size and latency exceed the separate resource criteria. This is a research demonstration, not an operational protection system.

From the repository root, with Python **3.14.7**:

```text
python -m venv .venv
.venv\Scripts\python -m pip install -r deployment/requirements.txt
.venv\Scripts\python -B -m src.inference.cli --input deployment/example_input.json
.venv\Scripts\python -B -m unittest discover -s tests -v
```

On POSIX use `.venv/bin/python` after creating the environment. The preserved pickle requires exact recorded versions; installation on an unsupported Python/platform is not claimed. Only the supplied model is accepted, and its fixed SHA-256 is checked before loading. Pickle is executable serialization; arbitrary replacement artifacts are unsupported.

Input: one JSON object, exactly `vdc1`, `vdc2` in volts and `idc1`, `idc2` in amperes. Values must be finite nonnegative numbers. Nulls, strings, booleans, missing channels, timestamps, target labels and additional columns are rejected. Irradiance and temperature are not inputs to E4. Missing-channel simulation in archived research does not imply that this CLI accepts missing sensors.

| Channel | Observed TRAIN range | Unit |
| --- | --- | --- |
| vdc1 | 0.3799?363.974 | V |
| vdc2 | 0.3164?368.749 | V |
| idc1 | 0.0418?9.6549 | A |
| idc2 | 0.0046?9.4987 | A |

These are rounded observed ranges, not certified operating limits. Outside-range inputs produce a warning and are not clipped. Original quality rules, TRAIN medians and all four missing indicators are loaded with the fitted model. No preprocessing is refitted. The forest has eight mathematical inputs but requires four physical channels.

Output contains predicted class, human-readable label, hardware-fault classification flag, environmental-shade flag, model version/hash and range warnings. Class 4 is natural building shade, not hardware failure. The flag describes argmax class membership, not the separately thresholded research alert rule. No calibrated confidence is returned. The [example output](example_output.json) is an actual execution on [example input](example_input.json), selected from a released raw observation; the model is not required to agree with the true class. No target is passed to inference. Five additional [released-observation cases](example_cases.json), sampled across the true classes for coverage, record actual predictions without passing true labels into the model.

[Scientific protocol and limitations](../reports/Model_Selection_and_Deployment.md) ? [Model provenance](../models/rf_e4/provenance.json)
