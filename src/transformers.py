"""Existing target-free quality, physical-feature and availability transformations."""
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
SENSORS=['vdc1','vdc2','idc1','idc2','irr','pvt']
DEPENDENCIES={'P1':['vdc1','idc1'],'P2':['vdc2','idc2'],'P_total':['vdc1','idc1','vdc2','idc2'],'V_diff':['vdc1','vdc2'],'I_diff':['idc1','idc2']}
class RetainedQuality(TransformerMixin,BaseEstimator):
 def __init__(self,channels):self.channels=channels
 def fit(self,X,y=None):
  # Quality fitting only validates retained schema; no learned statistics or extra channel access.
  if list(X.columns)!=list(self.channels):raise ValueError('Retained channel schema mismatch')
  self.feature_names_in_=np.array(self.channels,dtype=object);return self
 def transform(self,X):
  if list(X.columns)!=list(self.channels):raise ValueError('Removed channels cannot enter preprocessing')
  z=X.copy().astype(float);z=z.mask(~np.isfinite(z))
  for c in self.channels:
   if c.startswith(('vdc','idc')):z.loc[z[c]<0,c]=np.nan
   if c=='irr':
    z.loc[z[c]<-1,c]=np.nan;z.loc[(z[c]>=-1)&(z[c]<0),c]=0.
  return z
 def get_feature_names_out(self,input_features=None):return np.array(self.channels,dtype=object)

class PhysicalFeatures(TransformerMixin,BaseEstimator):
 def __init__(self,channels=None):self.channels=channels
 def fit(self,X,y=None):
  self.channels_=list(SENSORS if self.channels is None else self.channels)
  if len(set(self.channels_))!=len(self.channels_) or not set(self.channels_)<=set(SENSORS):raise ValueError('Invalid physical channels')
  if np.asarray(X).shape[1]!=len(self.channels_):raise ValueError('Feature/channel shape mismatch')
  self.derived_=[k for k,v in DEPENDENCIES.items() if set(v)<=set(self.channels_)]
  self.n_features_in_=len(self.channels_);return self
 def transform(self,X):
  a=np.asarray(X,dtype=float)
  if a.ndim!=2 or a.shape[1]!=self.n_features_in_:raise ValueError('Feature/channel shape mismatch')
  v={c:a[:,i] for i,c in enumerate(self.channels_)};out=[a]
  with np.errstate(over='raise',invalid='raise'):
   for f in self.derived_:
    if f=='P1':d=v['vdc1']*v['idc1']
    elif f=='P2':d=v['vdc2']*v['idc2']
    elif f=='P_total':d=v['vdc1']*v['idc1']+v['vdc2']*v['idc2']
    elif f=='V_diff':d=np.abs(v['vdc1']-v['vdc2'])
    else:d=np.abs(v['idc1']-v['idc2'])
    out.append(d[:,None])
  result=np.column_stack(out)
  if not np.isfinite(result).all():raise ValueError('Nonfinite physical feature; review input/imputation.')
  return result
 def get_feature_names_out(self,input_features=None):return np.array(self.channels_+self.derived_,dtype=object)

def eligible(clean,boundaries):
 missing=clean.isna().to_numpy();pos=np.arange(len(clean));idx=clean.index.to_numpy()
 if not len(clean):return np.zeros(0,dtype=bool)
 reset=np.r_[True,np.diff(idx)!=1]|np.isin(idx,boundaries);runs=np.zeros_like(missing,dtype=np.int64)
 for j in range(missing.shape[1]):
  last=np.maximum.accumulate(np.where(~missing[:,j],pos,np.where(reset,pos-1,-1)))
  runs[:,j]=np.where(missing[:,j],pos-last,0)
 return (missing.sum(axis=1)<=1)&(runs.max(axis=1)<=2)
