"""Dependency-free HTTP checks of the running approved Linux identity image."""
import json,os,time,urllib.request,urllib.error
from pathlib import Path
BASE='http://127.0.0.1:8768'
ROOT=Path(__file__).resolve().parents[2]
SHA='55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb'
def request(path,method='GET',value=None,headers=None,raw=None):
 h=dict(headers or {});data=raw if raw is not None else json.dumps(value).encode() if value is not None else None
 if data is not None:h['Content-Type']='application/json'
 req=urllib.request.Request(BASE+path,data=data,headers=h,method=method)
 try:
  with urllib.request.urlopen(req,timeout=15) as r:return r.status,r.read(),{k.lower():v for k,v in r.headers.items()}
 except urllib.error.HTTPError as e:return e.code,e.read(),{k.lower():v for k,v in e.headers.items()}
def main():
 for _ in range(90):
  try:
   status,body,_=request('/api/health')
   if status==200:break
  except (OSError,TimeoutError):pass
  time.sleep(1)
 else:raise RuntimeError('Identity container did not become ready')
 assert json.loads(body)['model_sha256']==SHA
 status,body,h=request('/');assert status==200 and b'PV Intelligence API' in body and b'id="prediction-form"' not in body
 assert "default-src 'self'" in h['content-security-policy'] and 'unsafe-inline' not in h['content-security-policy']
 for asset in ['backend.css','backend.js','api.js']:assert request('/assets/'+asset)[0]==200
 for path in ['/docs','/redoc','/openapi.json']:assert request(path)[0]==404
 assert len(json.loads(request('/api/examples')[1]))==5
 cases=json.loads((ROOT/'deployment/example_cases.json').read_text());parity=[]
 for case in cases:
  status,body,_=request('/api/predict','POST',case['input']);value=json.loads(body);assert status==200 and all(value[k]==v for k,v in case['output'].items());parity.append(value['predicted_class'])
 origins=json.loads(os.environ['PV_FRONTEND_ORIGINS']);assert len(origins)==6;cors=[]
 for origin in origins+['https://unrelated.invalid']:
  status,_,h=request('/api/predict','OPTIONS',headers={'Origin':origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'});allowed=origin in origins
  assert status==(200 if allowed else 400);assert h.get('access-control-allow-origin')==(origin if allowed else None);assert 'access-control-allow-credentials' not in h;cors.append({'origin':origin,'HTTP':status})
 invalid=[];good=cases[0]['input']
 for name,value in [('missing',{}),('target',{**good,'f_nv':0}),('negative',{**good,'idc1':-1}),('boolean',{**good,'idc1':True})]:
  assert request('/api/predict','POST',value)[0]==422;invalid.append(name)
 for name,raw,expected in [('duplicate',b'{"vdc1":1,"vdc1":2}',422),('nonfinite',b'{"idc1":NaN}',422),('oversize',b'x'*2049,413)]:
  assert request('/api/predict','POST',raw=raw)[0]==expected;invalid.append(name)
 report={'status':'PASS','scope':'Actual Linux image HTTP; no optional TestClient dependency or runtime package changes','root_identity':True,'asset_routes':True,'security_headers':True,'docs_remain_disabled':True,'five_classes':parity,'CORS':cors,'invalid_payloads_rejected':invalid,'model_sha256':SHA}
 print('PV_IDENTITY_HTTP_BEGIN');print(json.dumps(report,indent=2));print('PV_IDENTITY_HTTP_END')
if __name__=='__main__':main()
