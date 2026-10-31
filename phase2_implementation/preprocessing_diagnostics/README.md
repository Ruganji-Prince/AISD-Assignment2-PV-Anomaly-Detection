# Preprocessing diagnostics

All eight original 300-DPI images are retained byte-for-byte. Populations and sampling are documented in [the diagnostic inventory](../compliance/Diagnostic_Inventory.json). All learned statistics use TRAIN only. Feature-to-target importance is mutual information, not trained predictive-model importance.

Figure 7 retains its original algorithm-oriented labels: “selected LR” identifies the standardized preprocessing branch; RF/LightGBM identify native-scale rationale. These labels describe intended algorithm requirements, not performance, selection results or current-stage classifier execution. Figure 3 compares raw and reference-cleaned values without statistical capping/deletion; Figure 8 is mathematical PCA, not a physical sensor reduction result.
