#  raw data CSV

[pv_fault_dataset.csv](pv_fault_dataset.csv) contains all 1,373,798 original source positions and seven columns, in source order. It is a CSV conversion of the paired original MAT inputs, not a cleaned/processed/model-generated dataset. No row, measurement or label was changed; no timestamp/index field was invented.

Columns: vdc1/vdc2 (V), idc1/idc2 (A), irr (W/m²), pvt (°C), and nominal f_nv (0 normal, 1 short circuit, 2 resistive degradation, 3 open circuit, 4 building shade).

Original source: [clayton-h-costa/pv_fault_dataset](https://github.com/clayton-h-costa/pv_fault_dataset), commit e9ed8ad8072dcb3ffc643b0f3604219798708551. Dataset attribution references [Lazzaretti et al. (2020)](https://doi.org/10.3390/s20174688); the [original Apache-2.0 license](../../phase1_strategy/PRIMARY_SOURCE_LICENSE.txt) and [source README](../../phase1_strategy/PRIMARY_SOURCE_README.md) are retained.

Size: 64,143,812 bytes (61.17 MiB). Its explicit publication was approved; downloading is appropriate for inspecting this large CSV. SHA-256: 717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a.

The 62 paired zeros, -0.0381 irradiance value and negative Celsius readings remain unmodified. Original MAT/candidate files remain ignored. The isolated Phase 1 audit reproduction route in the root README supports retrieval and auditing of pinned MAT sources without changing approved evidence.
