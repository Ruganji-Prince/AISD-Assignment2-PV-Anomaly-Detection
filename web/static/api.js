// Transport/readiness only. No model, fitted transformation or substitute prediction.
const config=globalThis.PV_CONFIG||{};
const base=config.apiBase||'';
if(base&&!/^https:\/\/pv-anomaly-detection\.wittygrass-37610045\.francecentral\.azurecontainerapps\.io$/.test(base)&&!/^http:\/\/(localhost|127\.0\.0\.1):[0-9]+$/.test(base))throw new Error('Unapproved inference API origin.');
export const apiURL=path=>base+path;
const startupLimit=120000, requestLimit=30000;
let pending=null,ready=false,readyAt=0;
const callbacks=new Set();
export function subscribeService(callback){callbacks.add(callback);return()=>callbacks.delete(callback);}
function state(name,message){for(const callback of callbacks)callback(name,message);}
export function invalidateService(){ready=false;}
async function timedFetch(path,options={},timeout=requestLimit){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeout);
 try{const response=await fetch(apiURL(path),{...options,credentials:'omit',cache:'no-store',signal:controller.signal});const text=await response.text();let body;try{body=JSON.parse(text);}catch{throw new Error('The cloud service returned an invalid response. Retry the connection.');}return {ok:response.ok,status:response.status,json:async()=>body};}
 finally{clearTimeout(timer);}
}
export function ensureReady({force=false}={}){
 if(pending)return pending;
 if(ready&&!force&&performance.now()-readyAt<30000)return Promise.resolve();
 ready=false;
 const startingTimer=setTimeout(()=>state('starting','Starting cloud inference service. This may take approximately one minute.'),1500);
 pending=(async()=>{
  const start=performance.now();state('connecting','Connecting to cloud inference service...');
  let attempt=0;
  while(performance.now()-start<startupLimit){
   if(attempt)state('starting','Starting cloud inference service. This may take approximately one minute.');
   const remaining=startupLimit-(performance.now()-start);
   try{
    const response=await timedFetch('/api/health',{},Math.min(requestLimit,remaining));
    if(response.ok){const body=await response.json();if(body.status==='ready'&&body.model_sha256==='55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb'){ready=true;readyAt=performance.now();state('ready','Model ready');return;}}
   }catch{/* Transient network/startup failures are retried only inside this bounded attempt. */}
   attempt++;const left=startupLimit-(performance.now()-start);if(left>0)await new Promise(resolve=>setTimeout(resolve,Math.min(2000,left)));
  }
  state('unavailable','Cloud inference service is unavailable. Retry the connection.');
  throw new Error('Cloud startup timed out. Retry the connection before running inference.');
 })().finally(()=>{clearTimeout(startingTimer);pending=null;});
 return pending;
}
export async function fetchExamples(){const response=await timedFetch('/api/examples');if(!response.ok)throw new Error('Dataset examples unavailable.');return response.json();}
export async function requestPrediction(values){
 await ensureReady();
 try{
  const response=await timedFetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(values)},60000);
  const result=await response.json();
  if(!response.ok){if(response.status>=500)invalidateService();throw new Error(typeof result.detail==='string'?result.detail:'Unable to analyze these measurements.');}
  return result;
 }catch(error){if(error.name==='AbortError'||error instanceof TypeError){invalidateService();state('unavailable','Cloud inference service is unavailable. Retry the connection.');}throw error;}
}
