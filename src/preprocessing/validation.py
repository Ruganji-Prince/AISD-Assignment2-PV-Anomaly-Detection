"""Reference consistency checks; no fitted predictive estimator required."""
import numpy as np
from .common import load
def validate_study(study):
 ref=load('phase2_implementation/compliance/Preprocessing_Reference.json')
 for key in ['raw_audit','splits','reference_cleaning']:
  assert study.stats[key]==ref[key],key
 for key,row in ref['model_ready'].items():
  got=study.stats['model_ready'][key]
  assert got==row,key
 assert np.allclose(study.correlation,ref['correlation']['matrix'],rtol=0,atol=1e-12)
 assert np.allclose(study.mi,list(ref['mutual_information']['scores_nats'].values()),rtol=0,atol=1e-10)
 assert np.allclose(study.pca.explained_variance_ratio_,ref['PCA']['explained_variance_ratio'],rtol=0,atol=1e-10)
 for key in ['standard_mean','standard_scale','robust_center','robust_scale','minmax_data_min','minmax_data_max']:
  assert np.allclose(study.stats['scaling'][key],ref['scaling'][key],rtol=0,atol=1e-10),key
