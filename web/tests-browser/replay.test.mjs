import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {Replay,validateReplay} from '../static/replay.js';
const data=JSON.parse(fs.readFileSync(new URL('../data/pv_historical_replay.json',import.meta.url)));
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
class Clock{
 now=0;next=0;jobs=new Map();
 set=(fn,ms)=>{const id=++this.next;this.jobs.set(id,{fn,due:this.now+ms});return id;};
 clear=id=>this.jobs.delete(id);
 async advance(ms){const end=this.now+ms;for(;;){const next=[...this.jobs].sort((a,b)=>a[1].due-b[1].due)[0];if(!next||next[1].due>end)break;this.now=next[1].due;this.jobs.delete(next[0]);next[1].fn();await flush();}this.now=end;await flush();}
}
function fixture(extra={}){
 const clock=new Clock(),calls=[],results=[],states=[],observations=[];
 const replay=new Replay({load:async()=>data,ready:async()=>{},infer:async values=>{calls.push(values);return {predicted_class:4};},onResult:(r,o)=>results.push({prediction:r.predicted_class,source:o.source_class}),onState:(s,m,n)=>states.push({s,m,n}),onObservation:(o,n)=>observations.push({o,n}),setTimer:clock.set,clearTimer:clock.clear,...extra});
 return {clock,calls,results,states,observations,replay};
}
test('real replay validates all150 including all13 recorded disagreements',()=>{
 assert.equal(validateReplay(data),data);
 const proof=JSON.parse(fs.readFileSync(new URL('../../technical_evaluation/PV_Replay_Verification.json',import.meta.url)));
 assert.equal(proof.observations.filter(r=>!r.agrees_with_source).length,13);
 data.observations.forEach((r,i)=>{assert.equal(r.source_class,proof.observations[i].ground_truth_class);for(const k of ['vdc1','vdc2','idc1','idc2'])assert.equal(r.measurements[k],proof.observations[i][k]);});
});
test('invalid, duplicated and extra-field historical data rejected',()=>{
 for(const mutate of [x=>x.observations.pop(),x=>x.observations[0].measurements.idc1=Infinity,x=>x.observations[0].measurements.f_nv=1,x=>x.observations[1]=structuredClone(x.observations[0])]){const copy=structuredClone(data);mutate(copy);assert.throws(()=>validateReplay(copy));}
});
test('no scheduler traffic without explicit Start',async()=>{const f=fixture();await f.clock.advance(100000);assert.equal(f.calls.length,0);assert.equal(f.replay.cursor,0);});
test('native browser timers retain the global receiver',async()=>{
 const oldSet=globalThis.setTimeout,oldClear=globalThis.clearTimeout;
 globalThis.setTimeout=function(...args){assert.equal(this,globalThis);return oldSet(...args);};
 globalThis.clearTimeout=function(...args){assert.equal(this,globalThis);return oldClear(...args);};
 const replay=new Replay({load:async()=>data,ready:async()=>{},infer:async()=>({predicted_class:0})});
 try{await replay.start();assert.equal(replay.cursor,1);replay.pause();}finally{globalThis.setTimeout=oldSet;globalThis.clearTimeout=oldClear;}
});
test('25bounded sequential observations contain five classes and exact payloads',async()=>{
 const f=fixture();await f.replay.start();for(let i=1;i<25;i++)await f.clock.advance(5000);
 assert.equal(f.calls.length,25);assert.equal(f.replay.cursor,25);assert.equal(f.states.at(-1).s,'completed');
 assert.deepEqual(f.calls,data.observations.slice(0,25).map(r=>r.measurements));
 assert.equal(new Set(f.observations.map(r=>r.o.source_class)).size,5);
 for(const r of f.results)assert.equal(r.prediction,4); // Transport output, never source label.
 await f.clock.advance(1000000);await f.replay.start();assert.equal(f.calls.length,25);
});
test('next delay starts after inference resolves, never overlaps',async()=>{
 const pending=deferred();let n=0;const f=fixture({infer:()=>{n++;return n===1?pending.promise:Promise.resolve({predicted_class:0});}});
 const running=f.replay.start();await flush();await f.clock.advance(20000);assert.equal(n,1);
 pending.resolve({predicted_class:2});await running;await f.clock.advance(4999);assert.equal(n,1);await f.clock.advance(1);assert.equal(n,2);
});
test('Pause cancels waiting and no future requests are made',async()=>{const f=fixture();await f.replay.start();f.replay.pause();await f.clock.advance(60000);assert.equal(f.calls.length,1);assert.equal(f.clock.jobs.size,0);});
test('Pause invalidates late response and resume retries same observation',async()=>{
 const pending=deferred();let signal;const f=fixture({infer:(v,s)=>{signal=s;return pending.promise;}});
 const work=f.replay.start();await flush();f.replay.pause();assert(signal.aborted);pending.resolve({predicted_class:1});await work;
 assert.equal(f.results.length,0);assert.equal(f.replay.cursor,0);f.replay.infer=async()=>({predicted_class:2});await f.replay.start();assert.equal(f.results[0].prediction,2);assert.equal(f.replay.cursor,1);
});
test('Restart clears counter and invalidates previous generation',async()=>{
 const f=fixture();await f.replay.start();await f.clock.advance(5000);assert.equal(f.replay.cursor,2);
 const ready=deferred();f.replay.ready=()=>ready.promise;const work=f.replay.restart();await flush();assert.equal(f.replay.cursor,0);assert.equal(f.states.at(-1).n,0);ready.resolve();await work;assert.deepEqual(f.calls.at(-1),data.observations[0].measurements);
});
test('repeated Start does not duplicate in-flight work',async()=>{const d=deferred();let calls=0;const f=fixture({infer:()=>{calls++;return d.promise;}});const a=f.replay.start();await flush();await f.replay.start();assert.equal(calls,1);d.resolve({predicted_class:0});await a;assert.equal(f.clock.jobs.size,1);});
test('load/readiness/API failures stop with no invented result',async()=>{
 for(const name of ['load','ready','infer']){const f=fixture({[name]:async()=>{throw new Error('offline');}});await f.replay.start();assert.equal(f.states.at(-1).s,'error');assert.equal(f.results.length,0);await f.clock.advance(100000);assert.equal(f.clock.jobs.size,0);}
});
test('cancel during readiness prevents any inference',async()=>{const ready=deferred();const f=fixture({ready:()=>ready.promise});const work=f.replay.start();await flush();f.replay.pause();ready.resolve();await work;assert.equal(f.calls.length,0);});
test('API AbortSignal cancels health and prevents retry traffic',async()=>{
 const oldFetch=globalThis.fetch;let requests=0;const api=await import('../static/api.js?abort-readiness');
 globalThis.fetch=(url,options)=>{requests++;return new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')),{once:true}));};
 try{const controller=new AbortController();const work=api.ensureReady({signal:controller.signal});await flush();controller.abort();await assert.rejects(work,{name:'AbortError'});assert.equal(requests,1);}finally{globalThis.fetch=oldFetch;api.cancelServiceCheck();}
});
test('API forwards only supplied four channels and aborts active fetch',async()=>{
 const oldFetch=globalThis.fetch;const api=await import('../static/api.js?abort-predict');let payload,entered=deferred();
 globalThis.fetch=async(url,options)=>{if(String(url).endsWith('/health'))return new Response(JSON.stringify({status:'ready',model_sha256:'55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb'}));payload=JSON.parse(options.body);entered.resolve();return new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')),{once:true}));};
 try{const c=new AbortController();const p=api.requestPrediction(data.observations[0].measurements,{signal:c.signal});await entered.promise;c.abort();await assert.rejects(p,{name:'AbortError'});assert.deepEqual(payload,data.observations[0].measurements);}finally{globalThis.fetch=oldFetch;api.cancelServiceCheck();}
});
