import numpy as np
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix,average_precision_score,log_loss

def reliability(y,s,n_bins=10):
 y=np.asarray(y,dtype=float);s=np.asarray(s);bins=np.minimum((np.clip(s,0,1)*n_bins).astype(int),n_bins-1);rows=[]
 for b in range(n_bins):
  mask=bins==b;count=int(mask.sum())
  rows.append({'bin':b,'lower':b/n_bins,'upper':(b+1)/n_bins,'N':count,'mean_probability':float(s[mask].mean()) if count else None,'observed_frequency':float(y[mask].mean()) if count else None})
 ece=sum(r['N']/len(y)*abs(r['mean_probability']-r['observed_frequency']) for r in rows if r['N']) if len(y) else None
 return {'N':len(y),'ECE':ece,'binning':'10 fixed equal-width bins; weighted absolute probability-frequency gap','bins':rows}

def probability_metrics(p,y):
 p=np.asarray(p);y=np.asarray(y,dtype=int);ok=np.isfinite(p).all(1)
 if not ok.all():return {'status':'NOT_APPLICABLE','reason':'Probability quality reported only for fully covered populations; abstentions present.','coverage':float(ok.mean())}
 q=np.maximum(p,1e-12);q/=q.sum(1,keepdims=True);one=np.eye(5)[y];pred=q.argmax(1);confidence=q.max(1)
 return {'status':'VERIFIED','N':len(y),'multiclass_Brier':float(np.mean(np.sum((q-one)**2,axis=1))),'Brier_definition':'mean_i sum_k (p_ik - 1[y_i=k])^2; range [0,2], not divided by classes','log_loss':float(log_loss(y,q,labels=np.arange(5))),'top_label_reliability':reliability(pred==y,confidence),'class_reliability':{str(k):reliability(y==k,q[:,k]) for k in range(5)},'hardware_reliability':reliability(np.isin(y,[1,2,3]),q[:,1:4].sum(1))}

def evaluate(p,y,threshold=None):
 p=np.asarray(p);y=np.asarray(y,dtype=int);ok=np.isfinite(p).all(1);z=np.nan_to_num(p,nan=0.);pred=z.argmax(1);pred[~ok]=-1
 pr,re,f1,n=precision_recall_fscore_support(y,pred,labels=np.arange(5),zero_division=0);cm=confusion_matrix(y,pred,labels=[0,1,2,3,4,-1])[:5]
 per={str(k):{'N':int(n[k]),'base_rate':float(n[k]/len(y)),'precision':float(pr[k]) if (pred==k).any() else None,'recall':float(re[k]) if n[k] else None,'f1':float(f1[k]) if n[k] else None,'AP':float(average_precision_score(y==k,z[:,k])) if 0<n[k]<len(y) else None} for k in range(5)}
 present=n>0;score=z[:,1:4].sum(1);h=np.isin(y,[1,2,3]);alert=(score>=threshold)&ok if threshold is not None else np.isin(pred,[1,2,3]);k=max(1,int(np.ceil(len(y)*.01)));rank=np.argsort(-score,kind='stable')[:k]
 def rate(mask):return float(alert[mask].mean()) if mask.any() else None
 result={'N':len(y),'macro_f1_present_classes':float(f1[present].mean()),'macro_f1_fixed_five':float(f1.mean()),'weighted_f1':float(np.average(f1,weights=n)),'balanced_accuracy_present_classes':float(re[present].mean()),'macro_precision_present_classes':float(pr[present].mean()),'per_class':per,'coverage':float(ok.mean()),'confusion_matrix':cm.tolist(),'confusion_columns':[0,1,2,3,4,'abstain'],'macro_AP':float(np.mean([v['AP'] for v in per.values()])) if all(v['AP'] is not None for v in per.values()) else None,'hardware_AP':float(average_precision_score(h,score)) if h.any() and (~h).any() else None,'hardware_precision_at_top_1pct':float(h[rank].mean()),'top_1pct_N':k,'hardware_alert_recall':rate(h),'normal_FPR':rate(y==0),'shade_FPR':rate(y==4),'combined_nonhardware_FPR':rate(~h),'alert_rule':'p1+p2+p3 >= frozen threshold' if threshold is not None else 'argmax class in {1,2,3}; not a tuned alert threshold','threshold':threshold,'absent_true_classes':np.flatnonzero(~present).tolist(),'AP_definition':'one-vs-rest average precision; not trapezoidal PR-AUC','hardware_definition':'classes1/2/3 only; shade environmental'}
 return result

def hypothetical_cost(y,p,hardware_miss_weight=10):
 C=np.ones((5,5));np.fill_diagonal(C,0)
 for k in [1,2,3]:C[k,0]=hardware_miss_weight;C[k,4]=hardware_miss_weight*.8
 for k in [0,4]:C[k,1:4]=2 if k==0 else 3
 for k in [1,2,3]:
  for j in [1,2,3]:
   if k!=j:C[k,j]=3
 pred=np.nan_to_num(p,nan=0).argmax(1)
 return {'matrix':C.tolist(),'relative_loss_per_1000_observations':float(C[np.asarray(y,dtype=int),pred].mean()*1000),'units':'Explicitly hypothetical relative severity units, not monetary cost','hardware_miss_weight':hardware_miss_weight}
