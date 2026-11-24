"""Deterministic original-case CLI/API parity demonstration; no fitting or scenario search."""
import argparse,json,urllib.request,urllib.error
from pathlib import Path
from src.inference.cli import ROOT,SHA256,load_model,predict

def request(url,payload=None):
 data=None if payload is None else json.dumps(payload).encode()
 req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'} if data else {})
 try:
  with urllib.request.urlopen(req,timeout=60) as response:return response.status,json.loads(response.read()),dict(response.headers)
 except urllib.error.HTTPError as error:return error.code,None,dict(error.headers)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url',help='Optional local or public API base URL; omitted means completely offline CLI only.');args=parser.parse_args();model=load_model();cases=json.loads((ROOT/'deployment/example_cases.json').read_text());rows=[]
 if args.url:
  base=args.url.rstrip('/');status,health,_=request(base+'/api/health');assert status==200 and health['model_sha256']==SHA256
 for case in cases:
  local=predict(case['input'],model);assert local==case['output'];row={'reference_case':case['case'],'source':'Predetermined historical TEST reference; parity demonstration, not independent generalization evidence','measurements':case['input'],'CLI_class':local['predicted_class'],'label':local['label']}
  if args.url:
   status,remote,headers=request(base+'/api/predict',case['input']);assert status==200
   for key,value in local.items():assert remote[key]==value
   row.update(API_class=remote['predicted_class'],server_timing=next((v for k,v in headers.items() if k.lower()=='server-timing'),None))
  rows.append(row)
 invalid={'missing':{},'negative':dict(cases[0]['input'],idc1=-1),'unexpected_target':dict(cases[0]['input'],f_nv=0)}
 for name,record in invalid.items():
  try:predict(record,model)
  except (ValueError,TypeError):pass
  else:raise AssertionError('Invalid input accepted: '+name)
  if args.url:assert request(base+'/api/predict',record)[0]==422
 print(json.dumps({'status':'PASS','model_sha256':SHA256,'cases':rows,'invalid_inputs_rejected':list(invalid),'mode':'CLI/API parity' if args.url else 'Offline CLI; no network requests'},indent=2))
if __name__=='__main__':main()
