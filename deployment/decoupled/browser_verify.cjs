const {chromium}=require('playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'../..');const cases=JSON.parse(fs.readFileSync(path.join(root,'deployment/example_cases.json'),'utf8'));
const base=process.env.PV_APP_URL;const api=process.env.PV_API_URL||'https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io';const output=process.env.PV_EVIDENCE_DIR;
if(!base||!output)throw new Error('PV_APP_URL and fresh PV_EVIDENCE_DIR required');
const records=[];
(async()=>{
 const browser=await chromium.launch({headless:true});const context=await browser.newContext();const page=await context.newPage();const errors=[];
 page.on('pageerror',error=>errors.push(error.message));let requests=[];
 page.on('request',r=>{if(r.url().includes('/api/'))requests.push({url:r.url(),method:r.method()});});
 await page.addInitScript(()=>{window.pvServiceTimes={};new MutationObserver(()=>{const node=document.getElementById('service-status');const state=node?.dataset.state;if(state&&window.pvServiceTimes[state]===undefined)window.pvServiceTimes[state]=performance.now();}).observe(document,{subtree:true,attributes:true,childList:true});});
 const response=await page.goto(base,{waitUntil:'domcontentloaded',timeout:120000});assert.equal(response.status(),200);
 await page.locator('#service-status').filter({hasText:'Model ready'}).waitFor({timeout:130000});
 const pageTiming=await page.evaluate(()=>({navigation:Object.fromEntries(["name", "startTime", "duration", "nextHopProtocol", "fetchStart", "domainLookupStart", "domainLookupEnd", "connectStart", "connectEnd", "requestStart", "responseStart", "responseEnd", "domContentLoadedEventEnd", "loadEventEnd", "responseStatus", "decodedBodySize"].map(k=>[k,performance.getEntriesByType('navigation')[0][k]])),service:window.pvServiceTimes}));
 async function go(k){await page.click('#step-tab-'+k);await page.waitForFunction(k=>!document.getElementById('step-'+k).hidden&&document.getElementById('step-'+k).getAnimations().length===0,k);}
 const labels=await page.evaluate(async()=>{const source=await import('/assets/explanations.js');return source.labels;});
 for(let k=0;k<5;k++){
  await go(0);for(const [key,value] of Object.entries(cases[k].input))await page.fill('#'+key,String(value));await go(3);
  await page.evaluate(()=>{window.pvRendered=null;const node=document.getElementById('result-content');const observer=new MutationObserver(()=>{if(!node.hidden){window.pvRendered=performance.now();observer.disconnect();}});observer.observe(node,{attributes:true});});
  const waiting=page.waitForResponse(r=>r.url()===api+'/api/predict'&&r.request().method()==='POST');
  await page.evaluate(()=>{window.pvSubmissionStart=performance.now();document.getElementById('assessment-run').click();});
  const r=await waiting;const body=await r.json();assert.equal(r.status(),200);assert.equal(body.predicted_class,k);
  assert.deepEqual(r.request().postDataJSON(),cases[k].input);assert.equal(body.model_sha256,cases[k].output.model_sha256);
  await page.locator('#result-content').waitFor({state:'visible'});assert.equal(await page.textContent('#predicted-label'),labels[k]);
  const render=await page.evaluate(()=>({submission:window.pvSubmissionStart,rendered:window.pvRendered,duration:window.pvRendered-window.pvSubmissionStart}));
  const headers=await r.allHeaders();records.push({case:k,input:r.request().postDataJSON(),url:r.url(),method:r.request().method(),HTTP:r.status(),response:body,displayed_label:await page.textContent('#predicted-label'),server_timing:headers['server-timing'],Azure_instance:headers['x-pv-instance'],DOM_update_ms:render.duration});
 }
 // At most one inference is issued while a submission is pending.
 await go(0);let count=0;let release,seen;const entered=new Promise(r=>{seen=r;});await page.route(api+'/api/predict',async route=>{count++;seen();await new Promise(resolve=>{release=resolve;});await route.continue();});
 const waiting=page.waitForResponse(r=>r.url()===api+'/api/predict'&&r.request().method()==='POST');
 await page.evaluate(()=>{document.getElementById('prediction-form').requestSubmit();document.getElementById('prediction-form').requestSubmit();});
 await entered;await page.waitForFunction(()=>document.getElementById('predict-button').disabled);assert.equal(count,1);release();await waiting;await page.waitForFunction(()=>!document.getElementById('predict-button').disabled);await page.unroute(api+'/api/predict');
 // Block Azure; no locally manufactured prediction is permitted.
 await page.route(api+'/**',route=>route.abort('failed'));
 await page.evaluate(()=>document.getElementById('prediction-form').requestSubmit());
 await page.locator('#form-error').waitFor({state:'visible'});assert.equal(await page.$eval('#result-content',n=>n.hidden),true);
 await page.locator('#service-retry').waitFor({state:'visible'});assert.equal(await page.locator('#service-retry').isEnabled(),true);
 const blockedMessage=await page.textContent('#form-error');await page.unroute(api+'/**');
 await page.click('#service-retry');await page.locator('#service-status').filter({hasText:'Model ready'}).waitFor({timeout:130000});
 // No health polling continues after readiness.
 const before=requests.filter(r=>r.url===api+'/api/health').length;await page.clock.install();await page.clock.fastForward(300000);await page.waitForTimeout(50);
 assert.equal(requests.filter(r=>r.url===api+'/api/health').length,before);
 // Explicitly simulated startup failure, advanced with virtual time; Azure remains running.
 const failure=await context.newPage();await failure.clock.install();let blockedHealth=0;
 await failure.route(api+'/**',route=>{if(route.request().url().endsWith('/api/health'))blockedHealth++;return route.abort('failed');});
 await failure.goto(base,{waitUntil:'domcontentloaded',timeout:120000});await failure.clock.fastForward(121000);await failure.locator('#service-status').filter({hasText:'unavailable'}).waitFor({timeout:10000});
 const terminalCount=blockedHealth;await failure.clock.fastForward(300000);assert.equal(blockedHealth,terminalCount);assert(terminalCount<=61);assert.equal(await failure.locator('#service-retry').isVisible(),true);await failure.close();
 // A held browser request expires at the distinct inference deadline; no backend shutdown.
 const timeoutPage=await context.newPage();await timeoutPage.clock.install();await timeoutPage.goto(base,{waitUntil:'domcontentloaded',timeout:120000});await timeoutPage.locator('#service-status').filter({hasText:'Model ready'}).waitFor({timeout:130000});
 let releaseTimeout;const timeoutStarted=timeoutPage.waitForRequest(r=>r.url()===api+'/api/predict'&&r.method()==='POST');
 await timeoutPage.route(api+'/api/predict',async route=>{await new Promise(resolve=>{releaseTimeout=resolve;});try{await route.abort('failed');}catch{}});
 await timeoutPage.click('#predict-button');await timeoutStarted;await timeoutPage.clock.fastForward(61000);
 await timeoutPage.locator('#form-error').filter({hasText:'timed out'}).waitFor({timeout:10000});assert.equal(await timeoutPage.$eval('#result-content',node=>node.hidden),true);releaseTimeout();await timeoutPage.close();
 // Delayed real health checks show starting state without changing the backend.
 const starting=await context.newPage();await starting.setViewportSize({width:320,height:844});await starting.route(api+'/api/health',async route=>{await new Promise(r=>setTimeout(r,2500));await route.continue();});
 await starting.goto(base,{waitUntil:'domcontentloaded',timeout:120000});await starting.locator('#service-status').filter({hasText:'Starting cloud'}).waitFor({timeout:10000});
 assert((await starting.evaluate(()=>document.documentElement.scrollWidth))<=320);await starting.locator('#service-status').filter({hasText:'Model ready'}).waitFor({timeout:130000});await starting.close();
 // Browser-origin benchmark: actual cross-origin JSON calls, no Python/Vercel inference proxy.
 const bench=await page.evaluate(async({api,input})=>{const rows=[];for(let i=0;i<15;i++){const started=performance.now();const r=await fetch(api+'/api/predict',{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify(input)});const result=await r.json();rows.push({request:i,HTTP:r.status,predicted_class:result.predicted_class,API_round_trip_ms:performance.now()-started,Server_Timing:r.headers.get('server-timing'),Azure_instance:r.headers.get('x-pv-instance'),model_sha256:result.model_sha256});}return rows;},{api,input:cases[0].input});
 assert(bench.every(r=>r.HTTP===200&&r.predicted_class===0&&r.Server_Timing&&r.Azure_instance));
 assert(requests.filter(r=>r.url.includes('/api/')).every(r=>r.url.startsWith(api+'/')));assert.deepEqual(errors,[]);
 const report={status:'VERIFIED',frontend:base,API:api,page_timing:pageTiming,five_reference_predictions:records,API_requests:requests,duplicate_submissions_one_request:true,blocked_Azure_no_fallback:true,blocked_error:blockedMessage,retry_recovers:true,no_keepalive_after_ready:true,bounded_startup_failure:{simulation:'Browser network abort and virtual clock, no backend shutdown',health_attempts:terminalCount,stops_after_bound:true},starting_state_mobile_no_overflow:true,bounded_inference_timeout:true,browser_benchmark:bench,probabilities_not_fabricated:true,source_scope:'Predetermined historical TEST cases demonstrate deployment parity, not independent accuracy',page_errors:errors};
 fs.mkdirSync(output,{recursive:true});fs.writeFileSync(path.join(output,'Browser_Network_Verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:report.status,frontend:base,five_predictions:records.map(r=>r.response.predicted_class),network_destination:api,duplicate_submissions:count,blocked_Azure_no_fallback:true,bounded_failure_health_attempts:terminalCount,benchmark_successes:bench.length}));await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
