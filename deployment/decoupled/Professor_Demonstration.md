# Professor demonstration

1. Open the [production application](https://pv-anomaly-detection-prince-r-k.vercel.app), wait for Ready and open browser Developer Tools > Network. Filter by `api/predict`.
2. Follow the existing four steps and enter vdc1=300.031 V, vdc2=329.544 V, idc1=0.2247 A, idc2=0.1272 A. Submit once.
3. Inspect the actual HTTPS POST to `https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io/api/predict`. The JSON contains the four physical measurements, without a true target. Confirm status 200, returned predicted class 0 and model identity; the interface displays the response.
4. The browser downloads HTML/CSS/JavaScript from Vercel. Azure validates inputs, loads the unchanged fitted preprocessing and RF E4 model, computes inference and returns JSON. No model or Python runtime is in the [actual frontend output](Frontend_Deployment_Verification.json).
5. Inspect CORS preflight and response headers. The exact trusted frontend origin is permitted; arbitrary origins are rejected. Timing and instance headers are exposed without credentialed requests.
6. Review [all five reference requests](Browser_Network_Verification.json) and [parity](Prediction_Parity.csv). Class 4 is natural building shade, an environmental condition rather than hardware failure. Historical TEST examples demonstrate serving parity, not fresh generalization accuracy.
7. Discuss scale-to-zero: startup may take time, the interface shows Connecting/Starting/Ready/Unavailable, polling is bounded and Retry is available. Azure failure produces an error rather than a substitute prediction. No keepalive is used.

Independent deployment boundaries permit frontend updates without replacing the trained model. The verified static-only frontend is now live on the canonical production alias. See [architecture](Architecture.md), [measurements](Performance_Evaluation.md), [completed cutover](Production_Cutover_Plan.md) and [rollback](Rollback_Guide.md).
