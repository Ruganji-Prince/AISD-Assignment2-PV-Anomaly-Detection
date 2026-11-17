"""Lazy explainability support; no expensive analysis is run by Stage 1."""
import numpy as np
from .contracts import SENSORS,SEED
from .evaluation import evaluate

def native_importance(model):
 est=model.pipeline.named_steps['model'];values=getattr(est,'feature_importances_',None)
 if values is None:values=np.abs(est.coef_).mean(axis=0)
 return dict(zip(model.names(),np.asarray(values,dtype=float).tolist()))

def physical_permutation(model,X,y,repeats=3,seed=SEED):
 """Permute raw channels then rerun the entire pipeline, regenerating all derivatives."""
 rng=np.random.default_rng(seed);base=evaluate(model.predict_proba(X),y)['macro_f1'];out={}
 for c in SENSORS:
  loss=[]
  for _ in range(repeats):
   altered=X.copy();altered[c]=rng.permutation(altered[c].to_numpy())
   loss.append(base-evaluate(model.predict_proba(altered),y)['macro_f1'])
  out[c]={'mean_macro_f1_loss':float(np.mean(loss)),'repeats':loss}
 return out

def tree_shap(model,X,background=None):
 """Optional later Tree SHAP; import only when approved dependencies and budget exist."""
 if model.family!='LightGBM':raise ValueError('Stage 1 SHAP support is for selected LightGBM.')
 import shap
 data=None if background is None else model.transformed(background)
 explainer=shap.TreeExplainer(model.pipeline.named_steps['model'],data=data,model_output='raw',
  feature_perturbation='tree_path_dependent' if data is None else 'interventional')
 return explainer(model.transformed(X))
