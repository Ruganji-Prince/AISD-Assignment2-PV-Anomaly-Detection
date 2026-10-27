"""Deferred 300-DPI diagnostic functions with seeded scatter sampling."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from .contracts import SEED,CLASSES

def _save(fig,path):
 fig.tight_layout();fig.savefig(path,dpi=300,facecolor='white');plt.close(fig)

def state_scatter(frame,y,xcol,ycol,path,max_rows=10000,seed=SEED):
 rng=np.random.default_rng(seed);fig,ax=plt.subplots();y=np.asarray(y)
 for k,name in enumerate(CLASSES):
  ix=np.flatnonzero(y==k);ix=rng.choice(ix,size=min(len(ix),max_rows//5),replace=False)
  ax.scatter(frame.iloc[ix][xcol],frame.iloc[ix][ycol],s=3,alpha=.35,label=name)
 ax.set(xlabel=xcol,ylabel=ycol);ax.legend(fontsize=7);_save(fig,path)

def vi_scatter(frame,y,path,**kwargs):return state_scatter(frame,y,'vdc1','idc1',path,**kwargs)
def thermal_irradiance(frame,y,path,**kwargs):return state_scatter(frame,y,'irr','pvt',path,**kwargs)

def confusion_plot(matrix,path,normalized=False):
 m=np.asarray(matrix);fig,ax=plt.subplots();im=ax.imshow(m,cmap='Blues');fig.colorbar(im,ax=ax)
 ax.set(xlabel='Predicted state',ylabel='True state',xticks=range(m.shape[1]),yticks=range(5))
 for i in range(m.shape[0]):
  for j in range(m.shape[1]):ax.text(j,i,f'{m[i,j]:.2f}' if normalized else str(int(m[i,j])),ha='center',va='center',fontsize=7)
 _save(fig,path)

def class_metrics_plot(metrics,path):
 fig,ax=plt.subplots();x=np.arange(5)
 for i,key in enumerate(['precision','recall','f1']):ax.bar(x+(i-1)*.25,[metrics['per_class'][str(k)][key] for k in range(5)],.25,label=key)
 ax.set(xticks=x,xticklabels=CLASSES,ylim=(0,1),ylabel='Score');ax.tick_params(axis='x',rotation=25);ax.legend();_save(fig,path)

def pr_plot(probabilities,y,path):
 fig,ax=plt.subplots();y=np.asarray(y)
 for k,name in enumerate(CLASSES):
  p,r,_=precision_recall_curve(y==k,np.asarray(probabilities)[:,k]);ax.plot(r,p,label=name)
 ax.set(xlabel='Recall',ylabel='Precision');ax.legend(fontsize=7);_save(fig,path)

def ablation_plot(table,path):
 fig,ax=plt.subplots()
 for family,group in table.groupby('model'):ax.plot(group.physical_channels,group.macro_f1,'o',label=family)
 ax.set(xlabel='Physical raw channels',ylabel='Macro-F1');ax.legend();_save(fig,path)

def importance_plot(importance,path):
 items=sorted(importance.items(),key=lambda x:x[1]);fig,ax=plt.subplots();ax.barh([x[0] for x in items],[x[1] for x in items]);ax.set_xlabel('Importance (method documented separately)');_save(fig,path)

def shap_summary(values,path):
 import shap
 shap.plots.beeswarm(values,show=False);plt.gcf().savefig(path,dpi=300,bbox_inches='tight');plt.close()
