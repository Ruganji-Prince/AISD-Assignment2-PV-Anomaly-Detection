"""Sparse-channel pipelines cloned from frozen Stage 1 estimators, without tuning."""
import json,pickle
import numpy as np
from sklearn.base import BaseEstimator,TransformerMixin,clone
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer,MissingIndicator
from sklearn.preprocessing import StandardScaler
from src.phase2_stage1.features import PhysicalFeatures,eligible
from .contracts import *

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

class AblationModel:
 def __init__(self,family,config):
  if family not in FAMILIES or config not in CONFIGS:raise ValueError('Unapproved family/configuration')
  self.family=family;self.config=config;self.channels=list(CONFIGS[config]);self.feature_policy='engineered' if family=='LightGBM' else 'raw'
  with (ROOT/'.cache/stage1/models'/(family+'.pkl')).open('rb') as f:source=pickle.load(f)
  self.frozen_estimator_params=source.pipeline.named_steps['model'].get_params()
  estimator=clone(source.pipeline.named_steps['model'])
  if estimator.get_params()['class_weight']!=frozen_weights():raise ValueError('Stage 1 class weights changed')
  numeric=[('median',SimpleImputer(strategy='median',keep_empty_features=True))]
  if family=='LightGBM':numeric.append(('physical',PhysicalFeatures(self.channels)))
  if family=='LR':numeric.append(('scale',StandardScaler()))
  columns=ColumnTransformer([('numeric',Pipeline(numeric),self.channels),
   ('missing',MissingIndicator(features='all',error_on_new=False),self.channels)],remainder='drop',sparse_threshold=0)
  self.pipeline=Pipeline([('quality',RetainedQuality(self.channels)),('columns',columns),('model',estimator)])
  split=json.loads((ROOT/'phase1_strategy/Phase1_Split_Manifest.json').read_text())
  self.boundaries=tuple(sorted({v for b in split['operating_blocks'] for v in [b['start'],b['end_exclusive']]}))
 def fit(self,X,y):
  schema(X,self.channels,training=True)
  if counts(y)!=TRAIN_COUNTS:raise ValueError('Training labels/population changed')
  self.pipeline.fit(X,y);self.fit_index_digest_=index_digest(X.index);self.fit_rows_=len(X)
  self.classes_=self.pipeline.named_steps['model'].classes_
  assert self.pipeline.named_steps['model'].get_params()==self.frozen_estimator_params
  assert len(self.names())==available_features(self.config,self.family)['mathematical_feature_count']
  return self
 def predict_proba(self,X):
  schema(X,self.channels);clean=self.pipeline.named_steps['quality'].transform(X)
  p=self.pipeline[1:].predict_proba(clean);p[~eligible(clean,self.boundaries)]=np.nan;return p
 def names(self):return self.pipeline.named_steps['columns'].get_feature_names_out().tolist()
