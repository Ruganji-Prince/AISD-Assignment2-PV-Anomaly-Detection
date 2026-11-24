"""Standard-library-only actual Docker verifier for a local host or free Linux CI."""
import json,subprocess,time,urllib.request,urllib.error,os,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def command(*args):return subprocess.check_output(args,cwd=ROOT,text=True).strip()
def request(url,payload=None,body=None):
 data=json.dumps(payload).encode() if payload is not None else body;req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'} if data is not None else {})
 try:
  with urllib.request.urlopen(req,timeout=60) as r:return r.status,json.loads(r.read())
 except urllib.error.HTTPError as e:return e.code,None

def main():
 started=time.perf_counter();subprocess.run(['docker','build','-t','pv-rf-e4-verification','.'],cwd=ROOT,check=True);build_seconds=time.perf_counter()-started;image=json.loads(command('docker','image','inspect','pv-rf-e4-verification'))[0];name='pv-rf-e4-verification-'+str(os.getpid());startup=time.perf_counter()
 command('docker','run','-d','--read-only','--tmpfs','/tmp:rw,size=64m','-e','PYTHONDONTWRITEBYTECODE=1','-p','127.0.0.1:8768:8000','--name',name,'pv-rf-e4-verification')
 try:
  for _ in range(60):
   try:
    code,health=request('http://127.0.0.1:8768/api/health')
    if code==200:break
   except (OSError,ValueError):pass
   time.sleep(1)
  else:raise RuntimeError('Container never became healthy')
  startup_seconds=time.perf_counter()-startup;assert health['model_sha256']=='55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb';uid=int(command('docker','exec',name,'id','-u'));assert uid!=0;cases=json.loads((ROOT/'deployment/example_cases.json').read_text());results=[]
  for case in cases:
   code,result=request('http://127.0.0.1:8768/api/predict',case['input']);assert code==200;expected=case['output']['predicted_class'];assert result['predicted_class']==expected
   raw=command('docker','exec',name,'python','-B','-c','import json;from src.inference.cli import predict;print(json.dumps(predict(json.loads('+repr(json.dumps(case['input']))+'))))');assert json.loads(raw)['predicted_class']==expected
   code,live=request('https://pv-anomaly-detection-prince-r-k.vercel.app/api/predict',case['input']);assert code==200 and live['predicted_class']==expected;results.append({'case':case['case'],'container_API':expected,'container_CLI':expected,'Vercel_API':expected})
  good=cases[0]['input'];checks=[]
  for label,value in [('missing',{}),('extra',{**good,'f_nv':0}),('negative',{**good,'idc1':-1}),('nonfinite',{**good,'idc1':float('nan')})]:
   code,_=request('http://127.0.0.1:8768/api/predict',value);assert code==422;checks.append({'case':label,'status':code})
  for label,body,status in [('duplicate',b'{"vdc1":1,"vdc1":2}',422),('oversize',b'x'*2049,413)]:
   code,_=request('http://127.0.0.1:8768/api/predict',body=body);assert code==status;checks.append({'case':label,'status':code})
  runtime=json.loads(command('docker','exec',name,'python','-c','import json,platform;from importlib.metadata import version;print(json.dumps({"python":platform.python_version(),"platform":platform.platform(),"packages":{k:version(k) for k in ["numpy","pandas","scipy","scikit-learn","fastapi"]}}))'))
  report={'status':'VERIFIED','git_commit':os.environ.get('GITHUB_SHA','local'),'runner':'Standard ubuntu-latest public-repository runner' if os.environ.get('GITHUB_ACTIONS') else platform.platform(),'image_id':image['Id'],'image_bytes':image['Size'],'build_seconds':build_seconds,'startup_to_ready_seconds':startup_seconds,'nonroot_uid':uid,'read_only_root':True,'health':health,'runtime':runtime,'reference_cases':results,'invalid_checks':checks,'model_artifact_unchanged':True}
  print('PV_CONTAINER_BEGIN');print(json.dumps(report,indent=2));print('PV_CONTAINER_END')
 finally:subprocess.run(['docker','rm','-f',name],check=False)
if __name__=='__main__':main()
