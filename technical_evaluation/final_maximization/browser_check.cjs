const {chromium}=require('playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=process.env.PV_REPO_ROOT;const cases=JSON.parse(fs.readFileSync(path.join(root,'deployment/example_cases.json'),'utf8'));
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

 const layouts=[];for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:900});for(let k=0;k<4;k++){await go(k);assert(await page.locator('#step-'+k).isVisible());}assert((await page.evaluate(()=>document.documentElement.scrollWidth))<=width);layouts.push(width);}
 assert(requests.filter(r=>r.url.includes('/api/')).every(r=>r.url.startsWith(api+'/')));assert.deepEqual(errors,[]);
 const report={status:'PASS',frontend:base,API:api,five_reference_predictions:records,API_requests:requests,all_four_steps_visible: true,viewports_no_horizontal_overflow:layouts,page_errors:errors,scope:'New bounded live browser parity and navigation verification; full failure/accessibility evidence remains in docs/final-release.'};fs.mkdirSync(output,{recursive:true});fs.writeFileSync(path.join(output,'current_browser.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({status:'PASS',five_classes:records.map(r=>r.response.predicted_class),layouts}));await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
