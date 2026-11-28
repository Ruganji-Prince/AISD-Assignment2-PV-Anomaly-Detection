"""Preserve historical verifier; adapt its obsolete Vercel API check to Azure."""
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'technical_evaluation/refinement/container_verify.py'
source=path.read_text(encoding='utf8')
old='https://pv-anomaly-detection-prince-r-k.vercel.app/api/predict'
new='https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io/api/predict'
assert source.count(old)==1
source=source.replace(old,new).replace("'Vercel_API':expected","'Azure_API':expected")
print('PV_ORIGINAL_CHECK_ADAPTATION: only obsolete live Vercel API URL/label replaced by actual Azure inference endpoint; all assertions retained.',flush=True)
exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
