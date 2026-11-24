import argparse,asyncio,time,json,re,datetime
import httpx,numpy as np
from .runtime import stats
from .experiments import write
from technical_evaluation.common import ROOT,SHA
async def benchmark(url):
 cases=json.loads((ROOT/'deployment/example_cases.json').read_text());sample=cases[0]['input'];records=[]
 async with httpx.AsyncClient(timeout=60,follow_redirects=True,limits=httpx.Limits(max_connections=2,max_keepalive_connections=2)) as client:
  async def one(phase,i):
   start=time.perf_counter()
   try:r=await client.post(url+'/api/predict',json=sample)
   except httpx.HTTPError as exc:
    records.append({'phase':phase,'request':i,'HTTP':0,'error':type(exc).__name__,'network_ms':(time.perf_counter()-start)*1000,'server_timing_ms':{},'instance':None,'model_initialized':False});return
   elapsed=(time.perf_counter()-start)*1000;timing={k:float(v) for k,v in re.findall(r'([a-z_]+);dur=([0-9.]+)',r.headers.get('server-timing',''))};record={'phase':phase,'request':i,'HTTP':r.status_code,'network_ms':elapsed,'server_timing_ms':timing,'instance':r.headers.get('x-pv-instance'),'model_initialized':r.headers.get('x-pv-initialized')=='1'}
   if r.status_code==200:assert r.json()['predicted_class']==cases[0]['output']['predicted_class']
   records.append(record)
   if phase=='sequential' and i==0 and r.status_code>=500:
    write('results/failed_preview_benchmark.json',{'URL':url,'requests':records,'status':'STOPPED: first request server error'});raise RuntimeError('Preview unhealthy; stopped before further benchmark load')
  for i in range(30):await one('sequential',i)
  for i in range(0,12,2):await asyncio.gather(one('concurrency2',i),one('concurrency2',i+1))
  health=await client.get(url+'/api/health');assert health.status_code==200 and health.json()['model_sha256']==SHA
  parity=[]
  for case in cases:
   r=await client.post(url+'/api/predict',json=case['input']);assert r.status_code==200;assert r.json()['predicted_class']==case['output']['predicted_class'];parity.append({'case':case['case'],'class':r.json()['predicted_class']})
  invalid=[]
  for label,body in [('missing',{}),('extra',{**sample,'f_nv':0}),('negative',{**sample,'idc1':-1})]:r=await client.post(url+'/api/predict',json=body);assert r.status_code==422;invalid.append({'kind':label,'HTTP':r.status_code})
 result={'URL':url,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'total_benchmark_requests':42,'network':'Client timezone Africa/Johannesburg; physical egress not geolocated.','measurements':'All values are wall-clock. Server timing ends at response headers, excludes network transmission and initial module/platform startup; never billedCPU.','phases':{},'model_initialization_events':[r for r in records if r['model_initialized']],'cold_start':'X-PV-Initialized marks a verified model-cache load within a request, not full platform cold-start timing. Absence means no confirmed initialization in this run.','health':health.json(),'parity':parity,'invalid':invalid,'requests':records,'engineering_target_ms':10}
 for phase in ['sequential','concurrency2']:
  rows=[r for r in records if r['phase']==phase];good=[r for r in rows if r['HTTP']==200];warm=[r for r in good if not r['model_initialized']];out={'requests':len(rows),'successes':len(good),'failure_rate':1-len(good)/len(rows),'all_network':stats([r['network_ms'] for r in rows]),'warm_success_network':stats([r['network_ms'] for r in warm]) if warm else None,'warm_server_components':{}}
  for k in ['validation','frame','preprocessing','forest','server','body_validate']:
   a=[r['server_timing_ms'][k] for r in warm if k in r['server_timing_ms']]
   if a:out['warm_server_components'][k]=stats(a)
  result['phases'][phase]=out
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--receipt',default='results/cloud_profile.json');a=p.parse_args();r=asyncio.run(benchmark(a.url.rstrip('/')));write(a.receipt,r);print(json.dumps({'phases':r['phases'],'initialization_events':len(r['model_initialization_events'])},default=float,indent=2))
if __name__=='__main__':main()
