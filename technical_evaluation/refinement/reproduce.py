import argparse,subprocess,sys
from pathlib import Path
from technical_evaluation.common import ROOT
from .experiments import near,synthetic,uncertainty,calibration
from threadpoolctl import threadpool_limits

def main():
 p=argparse.ArgumentParser();p.add_argument('--reconstruct-all',action='store_true');a=p.parse_args();threadpool_limits(2);near();synthetic();uncertainty();calibration()
 if a.reconstruct_all:subprocess.run([sys.executable,'-B','-m','technical_evaluation.reconstruct','--candidate','all','--receipt','refinement/results/public_reconstruction_repeat.json'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-B','-m','technical_evaluation.refinement.verify'],cwd=ROOT,check=True)
if __name__=='__main__':main()
