"""Five-class and hardware metrics; Stage 1 never selects an alert threshold."""
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix,average_precision_score

def hardware_alert_metrics(scores,y,threshold,coverage=None):
 y=np.asarray(y);scores=np.asarray(scores);ok=np.isfinite(scores) if coverage is None else np.asarray(coverage,dtype=bool)
 alert=(np.nan_to_num(scores,nan=-np.inf)>=threshold)&ok;h=np.isin(y,[1,2,3]);tp=int((alert&h).sum());fp=int((alert&~h).sum());fn=int((~alert&h).sum())
 precision=tp/(tp+fp) if tp+fp else 0.;recall=tp/(tp+fn) if tp+fn else 0.
 def rate(mask):return float(alert[mask].mean()) if mask.any() else None
 return {'threshold':float(threshold),'precision':precision,'recall':recall,'f1':2*precision*recall/(precision+recall) if precision+recall else 0.,
 'normal_false_alarm_rate':rate(y==0),'shade_false_alarm_rate':rate(y==4),'combined_nonhardware_FPR':rate(~h),
 'hardware_class_alert_recall':{str(k):rate(y==k) for k in [1,2,3]},'TP':tp,'FP':fp,'FN':fn,'coverage':float(ok.mean())}

def evaluate(p,y,threshold=None):
 y=np.asarray(y);p=np.asarray(p);assert p.shape==(len(y),5)
 ok=np.isfinite(p).all(axis=1);z=np.nan_to_num(p,nan=0.);pred=z.argmax(axis=1);pred[~ok]=-1
 pr,re,f1,support=precision_recall_fscore_support(y,pred,labels=list(range(5)),zero_division=0)
 cm=confusion_matrix(y,pred,labels=[0,1,2,3,4,-1])[:5,:]
 norm=np.divide(cm,cm.sum(axis=1,keepdims=True),out=np.zeros_like(cm,dtype=float),where=cm.sum(axis=1,keepdims=True)>0)
 ap=[float(average_precision_score(y==k,z[:,k])) if np.any(y==k) else None for k in range(5)]
 hs=z[:,1:4].sum(axis=1);hs[~ok]=0.;h=np.isin(y,[1,2,3])
 result={'macro_f1':float(f1.mean()),'weighted_f1':float(np.average(f1,weights=support)),
 'per_class':{str(k):{'precision':float(pr[k]),'recall':float(re[k]),'f1':float(f1[k]),'support':int(support[k]),'AP':ap[k]} for k in range(5)},
 'macro_AP':float(np.mean(ap)) if None not in ap else None,'AP_definition':'One-vs-rest average precision; unweighted mean across five classes; not trapezoidal PR integration.',
 'confusion_matrix':cm.tolist(),'row_normalized_confusion_matrix':norm.tolist(),'confusion_columns':[0,1,2,3,4,'abstain'],
 'hardware_macro_recall':float(re[1:4].mean()),'hardware_to_normal':{str(k):{'count':int(cm[k,0]),'rate':float(cm[k,0]/support[k]) if support[k] else None} for k in [1,2,3]},
 'hardware_AP':float(average_precision_score(h,hs)) if h.any() else None,
 'hardware_score_definition':'p1 + p2 + p3; class 4 is environmental shade, not hardware failure.',
 'coverage':float(ok.mean()),'abstention_policy':'All-row recall counts abstentions as misses; AP assigns zero score.',
 'normal_classification_false_alarm_rate':float(np.mean(np.isin(pred[y==0],[1,2,3]))) if np.any(y==0) else None,
 'shade_classification_false_alarm_rate':float(np.mean(np.isin(pred[y==4],[1,2,3]))) if np.any(y==4) else None,
 'hardware_alert_metrics':None,'hardware_alert_status':'Deferred: block-14 threshold selection is not authorized in Stage 1.'}
 if threshold is not None:result['hardware_alert_metrics']=hardware_alert_metrics(hs,y,threshold,ok)
 return result
