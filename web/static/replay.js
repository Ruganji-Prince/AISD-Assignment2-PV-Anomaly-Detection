// Historical data and sequential scheduling only. Predictions always come from transport.
export const channels=['vdc1','vdc2','idc1','idc2'];
export function validateReplay(data){
 if(data?.schema_version!==1||data.source!=='historical TRAIN observations'||data.suggested_interval_ms!==5000||!Array.isArray(data.observations)||data.observations.length!==150)throw new Error('Historical replay data is invalid.');
 const counts=Array(5).fill(0),vectors=new Set();
 for(const row of data.observations){
  if(Object.keys(row).sort().join(',')!=='measurements,source_class'||!Number.isInteger(row.source_class)||row.source_class<0||row.source_class>4)throw new Error('Invalid historical source label.');
  if(!row.measurements||Object.keys(row.measurements).sort().join(',')!==[...channels].sort().join(',')||channels.some(k=>typeof row.measurements[k]!=='number'||!Number.isFinite(row.measurements[k])||row.measurements[k]<0))throw new Error('Invalid recorded measurements.');
  counts[row.source_class]++;vectors.add(JSON.stringify(channels.map(k=>row.measurements[k])));
 }
 if(counts.some(n=>n!==30)||vectors.size!==150)throw new Error('Historical replay coverage is invalid.');
 for(let i=0;i<150;i+=5)if(new Set(data.observations.slice(i,i+5).map(r=>r.source_class)).size!==5)throw new Error('Historical sequence is unbalanced.');
 return data;
}
export async function loadReplay(signal){
 const response=await fetch('/data/pv_historical_replay.json',{signal,credentials:'omit'});
 if(!response.ok)throw new Error('Recorded observations could not be loaded. Retry Start.');
 return validateReplay(await response.json());
}
export class Replay{
 constructor({load=loadReplay,ready,infer,onObservation=()=>{},onResult=()=>{},onState=()=>{},onCancel=()=>{},setTimer=setTimeout,clearTimer=clearTimeout,limit=25,delay=5000}){
  Object.assign(this,{load,ready,infer,onObservation,onResult,onState,onCancel,setTimer,clearTimer,limit,delay});
  this.cursor=0;this.generation=0;this.running=false;this.timer=null;this.controller=null;this.data=null;
 }
 current(g){return this.running&&g===this.generation&&!this.controller.signal.aborted;}
 pause(message='Paused. Press Start to resume.'){
  this.generation++;this.running=false;this.controller?.abort();this.clearTimer(this.timer);this.timer=null;this.onCancel();this.onState('paused',message,this.cursor);
 }
 reset(){this.pause();this.cursor=0;this.onState('idle','Ready. Press Start for a 25-observation demonstration.',0);}
 restart(){this.reset();return this.start();}
 async start(){
  if(this.running)return;
  if(this.cursor>=this.limit){this.onState('completed','25-observation demonstration complete. Choose Restart.',this.cursor);return;}
  this.running=true;const g=++this.generation;this.controller=new AbortController();const signal=this.controller.signal;
  this.onState('starting','Loading recorded observations and checking Azure readiness…',this.cursor);
  try{
   if(!this.data)this.data=await this.load(signal);
   if(!this.current(g))return;
   await this.ready(signal);
   if(this.current(g))await this.tick(g);
  }catch(error){this.fail(g,error);}
 }
 fail(g,error){
  if(!this.current(g))return;
  this.pause();this.onState('error','Replay stopped: '+(error.name==='AbortError'?'the request timed out. Retry Start.':error.message),this.cursor);
 }
 async tick(g){
  if(!this.current(g))return;
  try{
   const observation=this.data.observations[this.cursor];
   this.onState('predicting','Requesting the original model prediction…',this.cursor);
   this.onObservation(observation,this.cursor+1);
   const result=await this.infer({...observation.measurements},this.controller.signal);
   if(!this.current(g))return;
   this.onResult(result,observation,this.cursor+1);this.cursor++;
   if(this.cursor>=this.limit){this.running=false;this.onState('completed','25-observation demonstration complete. Choose Restart.',this.cursor);return;}
   this.onState('waiting','Prediction received. Next observation in approximately five seconds.',this.cursor);
   this.timer=this.setTimer(()=>{this.timer=null;void this.tick(g);},this.delay);
  }catch(error){this.fail(g,error);}
 }
}
