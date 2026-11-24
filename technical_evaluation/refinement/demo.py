"""Fixed TRAIN-derived demonstration, never search inputs for desired predictions."""
import argparse,json
from technical_evaluation.common import ROOT,original
from src.inference.cli import predict
from .experiments import load

def main():
 p=argparse.ArgumentParser();p.add_argument('--class',dest='condition',type=int,choices=range(5),default=0);p.add_argument('--seed',type=int,choices=[42,43,44,45,46],default=42);p.add_argument('--url');args=p.parse_args();data=load('refinement/results/empirical_scenarios.json');case=next(c for c in data['samples'] if c['seed']==args.seed and c['source_conditioning_class']==args.condition);result=predict(case['measurements'],original())
 if args.url:
  import httpx
  response=httpx.post(args.url.rstrip('/')+'/api/predict',json=case['measurements'],timeout=60);response.raise_for_status();remote=response.json();assert remote['predicted_class']==result['predicted_class'];result=remote
 print(json.dumps({'source':'TRAIN-derived empirical joint perturbation; first predetermined sample for this class/seed','source_conditioning_label':case['source_conditioning_class'],'not_validated_physical_simulation':True,'input':case['measurements'],'actual_model_output':result},indent=2))
if __name__=='__main__':main()
