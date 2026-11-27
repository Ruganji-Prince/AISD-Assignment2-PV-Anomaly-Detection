# Reused Azure API contract

Base URL: `https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io`. No prediction route or result field was invented for this architecture.

| Route | Method | Existing purpose |
| --- | --- | --- |
| /api/health | GET | Load/verify original model and return ready state, model SHA and Python version |
| /api/examples | GET | Five fixed source measurements and existing display names |
| /api/predict | POST | Validate four raw measurements and execute original fitted RF E4 pipeline |

Prediction input contains exactly finite nonnegative numeric `vdc1`, `vdc2` in V and `idc1`, `idc2` in A. Source-described DC RMS terminology is retained. No `f_nv`, timestamp, source index, operating block, irradiance, temperature or extra metadata is accepted by this selected four-channel contract. Basic client validation is not learned preprocessing; fitted transformations execute on Azure. Outside-training-range values produce existing warnings rather than silent client clipping.

```json
{"vdc1":300.031,"vdc2":329.544,"idc1":0.2247,"idc2":0.1272}
```

Actual response fields remain `predicted_class`, `label`, `hardware_fault_class`, `environmental_shade`, `model_version`, `model_sha256`, `range_warnings`, `fault_category` and `warnings`. Class order is0normal,1short circuit,2resistive degradation,3open circuit,4natural building shade. Integer codes remain nominal labels. Production uses original multiclass argmax; archived alert thresholds and experimental calibration are not deployed. No probability or confidence percentage is fabricated.

[Actual request and response bodies](Browser_Network_Verification.json) demonstrate all five outcomes. The five cases are historically exposed TEST observations and establish serving parity only.

Application safeguards remain:2048-byte body bound, duplicate-key/nonfinite/type rejection, five-second body deadline, fifteen-second inference response deadline, and two active inferences per process. Existing422/413/415/408/503/504 errors retain their meanings. The frontend's60-second normal request deadline and120-second bounded startup attempt are separate client-side controls, not changes to model inference.

CORS permits an explicit list of the necessary production aliases, verified preview and local development origins. JSON POST triggers OPTIONS preflight. Only GET/POST and Content-Type are requested; credentials are omitted. Server-Timing, X-PV-Instance, X-PV-Initialized and Retry-After are exposed for diagnostics. CORS is not authentication or distributed abuse prevention.
