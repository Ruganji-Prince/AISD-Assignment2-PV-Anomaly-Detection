"""Opt-in bounded public-endpoint verification; never changes cloud configuration."""
import datetime,json,time,platform
import httpx,numpy as np
from .common import *
URL='https://pv-anomaly-detection-prince-r-k.vercel.app'
def main():
 cases=json.loads((ROOT/'deployment/example_cases.json').read_text());timings=[];checks=[]
 with httpx.Client(timeout=90,follow_redirects=True) as client:
  home=client.get(URL);health=client.get(URL+'/api/health');assert home.status_code==200;assert health.json()['model_sha256']==SHA
  for case in cases:
   r=client.post(URL+'/api/predict',json=case['input']);assert r.status_code==200;result=r.json();assert result['predicted_class']==case['output']['predicted_class'];checks.append({'case':case['case'],'predicted_class':result['predicted_class'],'matches_original_CLI':True})
  record=cases[0]['input']
  invalid=[('missing',{}),('extra',{**record,'f_nv':0}),('negative',{**record,'idc1':-1}),('null',{**record,'idc1':None}),('string',{**record,'idc1':'4'})]
  for label,payload in invalid:
   r=client.post(URL+'/api/predict',json=payload);assert r.status_code==422;checks.append({'case':label,'status':r.status_code})
  for label,body in [('nonfinite',json.dumps(record).replace(str(record['idc1']),'NaN')),('oversized','x'*2050)]:
   r=client.post(URL+'/api/predict',content=body,headers={'content-type':'application/json'});assert r.status_code in [413,422];checks.append({'case':label,'status':r.status_code})
  for i in range(20):
   start=time.perf_counter();r=client.post(URL+'/api/predict',json=record);seconds=time.perf_counter()-start;timings.append({'sequence':i+1,'milliseconds':seconds*1000,'status':r.status_code});assert r.status_code==200
 a=np.array([t['milliseconds'] for t in timings]);warm=a[1:]
 write('evidence/rubric5/cloud.json',{'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'URL':URL,'health':health.json(),'public_frontend_HTTP':home.status_code,'checks':checks,'benchmark_requests':20,'successful':sum(t['status']==200 for t in timings),'failed':sum(t['status']!=200 for t in timings),'concurrency':1,'environment':platform.python_version()+' httpx sequential persistent client','network_location':'Client configured for Africa/Johannesburg; physical host/egress location not independently geolocated.','first_request_ms':a[0],'cold_start':'NOT VERIFIED: first benchmark request is not an identifiable cold start; health/parity requests preceded it.','model_only_cloud_latency':'NOT INSTRUMENTED; network round-trip timing must not be called model-only inference.','summary_ms':{'min':a.min(),'max':a.max(),'mean':a.mean(),'p50':np.quantile(a,.5),'p95':np.quantile(a,.95),'p99':np.quantile(a,.99)},'subsequent_19_ms':{'mean':warm.mean(),'p50':np.quantile(warm,.5),'p95':np.quantile(warm,.95),'p99':np.quantile(warm,.99)},'timings':timings,'baseline_repository_commit':load('Protected_Baseline.json')['baseline_commit'],'deployment_commit':'See separate authenticated Vercel project receipt; health does not expose Git commit.'})
 scenarios=[]
 for n in [1000,10000,100000,1000000]:
  cpu=n*.04/3600;memory=n*1*.2/3600
  scenarios.append({'requests':n,'assumed_active_CPU_seconds_per_request':.04,'assumed_allocated_GB':1,'assumed_in_flight_seconds_per_request':.2,'CPU_hours':cpu,'GB_hours':memory,'within_isolated_Hobby_allowances':cpu<=4 and memory<=360 and n<=1000000,'Hobby_charge':'No pay-as-you-go overage assumed; exceeding quotas can pause service.','illustrative_cpt1_Pro_gross_compute_USD_excluding_subscription_credits_taxes_transfer':cpu*.2+memory*.0166+n/1e6*.6})
 write('evidence/rubric5/cost.json',{'checked_date':'2026-11-24','official_sources':['https://vercel.com/docs/plans/hobby','https://vercel.com/docs/functions/usage-and-pricing'],'Hobby_allowances':{'CPU_hours':4,'GB_hours':360,'invocations':1000000,'CDN_requests':1000000,'transfer_GB':100},'pricing_reference':{'cpt1_CPU_USD_per_hour':.2,'cpt1_memory_USD_per_GB_hour':.0166,'Pro_invocations_USD_per_million':.6},'actual_charges':'NOT VERIFIED: no invoice/charge ledger inspected. No plan upgrade or purchase performed.','scenarios':scenarios,'limitations':'Illustrative isolated workload, not actual billed resource consumption. Compute duration, allocation, sharing, current usage, region, network transfer and other projects affect real quotas/costs; subscription and taxes omitted. Network latency is not active CPU time.'})
 print('CLOUD_API_AND_BENCHMARK_COMPLETE',flush=True)
