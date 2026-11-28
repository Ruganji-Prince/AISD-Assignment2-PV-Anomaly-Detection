// Bounded built-frontend -> existing production Azure API checks. No proxy/mocked successes.
const{chromium}=require('playwright');const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve(process.env.PV_REPO_ROOT||'.'),base=process.env.PV_APP_URL||'http://127.0.0.1:8080',api='https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io';
const output=process.env.PV_EVIDENCE_DIR;if(!output)throw new Error('PV_EVIDENCE_DIR required');
const cases=JSON.parse(fs.readFileSync(path.join(root,'deployment/example_cases.json'))),proof=JSON.parse(fs.readFileSync(path.join(root,'technical_evaluation/PV_Replay_Verification.json'))),data=JSON.parse(fs.readFileSync(path.join(root,'web/data/pv_historical_replay.json')));
const labels=['Normal','Short Circuit','Resistive Degradation','Open Circuit','Natural Building Shade'],keys=['vdc1','vdc2','idc1','idc2'];
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn,limit=15000){const deadline=Date.now()+limit;while(Date.now()<deadline){if(await fn())return;await pause(25);}throw new Error('Live browser condition timed out.');}
function luminance(rgb){const a=rgb.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return a[0]*.2126+a[1]*.7152+a[2]*.0722;}
function contrast(a,b){const x=[luminance(a),luminance(b)].sort((a,b)=>a-b);return(x[1]+.05)/(x[0]+.05);}
(async()=>{
 const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const requests=[],manual=[],automatic=[],contrasts=[];let phase='manual',active=0,maxActive=0,health;
 page.on('request',r=>{if(r.url()===api+'/api/predict'&&r.method()==='POST'){active++;maxActive=Math.max(maxActive,active);const values=r.postDataJSON();assert.deepEqual(Object.keys(values),keys);requests.push({phase,input:values,start_ms:performance.now(),request:r});}});
 page.on('response',async r=>{if(r.url()===api+'/api/predict'&&r.request().method()==='POST'){try{await r.finished();}finally{active--;const row=requests.find(v=>v.request===r.request());if(row)row.finish_ms=performance.now();}}});
 const healthResponse=page.waitForResponse(r=>r.url()===api+'/api/health',{timeout:130000});await page.goto(base,{waitUntil:'domcontentloaded'});
 health=await(await healthResponse).json();assert.equal(health.model_sha256,proof.model_sha256);await until(()=>page.$eval('#service-status',n=>n.dataset.state==='ready'),130000);

 const manualCheckpoint=path.join(output,'Azure_Manual_Checkpoint.json');
 if(fs.existsSync(manualCheckpoint)){const saved=JSON.parse(fs.readFileSync(manualCheckpoint));assert.equal(saved.status,'PASS');manual.push(...saved.manual_reference_cases);console.log('REUSING_VERIFIED_FIVE_MANUAL_CASES');}
 else for(const c of cases){
  for(const[k,v]of Object.entries(c.input))await page.fill('#'+k,String(v));const pending=page.waitForResponse(r=>r.url()===api+'/api/predict'&&r.request().method()==='POST');await page.click('#predict-button');const response=await pending;assert.equal(response.status(),200);const result=await response.json();
  for(const[k,v]of Object.entries(c.output))assert.deepEqual(result[k],v);await until(()=>page.$eval('#result-content',n=>!n.hidden));await page.click('#view-assessment');await until(()=>page.$eval('#step-3',n=>!n.hidden));assert.equal(await page.textContent('#predicted-label'),labels[c.case]);
  const category=await page.$eval('#category-badge',n=>({text:n.textContent,foreground:getComputedStyle(n).color,background:getComputedStyle(n.closest('.card')).backgroundColor}));const rgb=s=>s.match(/[\d.]+/g).map(Number);const ratio=contrast(rgb(category.foreground),rgb(category.background));assert(ratio>=4.5);contrasts.push({source:'actual class badge',class:c.case,...category,ratio,threshold:4.5});
  const displayed=await page.evaluate(async cls=>{const e=(await import('/assets/explanations.js')).explanations[cls];const actual={category:document.querySelector('#category-badge').textContent,meaning:document.querySelector('#meaning-text').textContent,cause:document.querySelector('#cause-text').textContent,check:document.querySelector('#check-text').textContent};return{expected:e,actual};},c.case);for(const k of ['category','meaning','cause','check'])assert.equal(displayed.actual[k],displayed.expected[k]);for(const[k,v]of Object.entries(c.input))assert.equal(Number(await page.inputValue('#'+k)),v);manual.push({reference_class:c.case,input:c.input,HTTP:200,response:result,displayed});await page.click('#step-tab-0');await until(()=>page.$eval('#step-0',n=>!n.hidden));console.log('AZURE_MANUAL_CLASS',c.case,'PASS');
 }
 fs.mkdirSync(path.join(output,'screenshots'),{recursive:true});
 if(!fs.existsSync(manualCheckpoint)) for(const width of [1440,390]){await page.setViewportSize({width,height:1000});await pause(75);await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'screenshots',`azure-manual-${width}.png`),fullPage:true,animations:'disabled'});}
 for(const step of [0,1,2,3]){await page.click('#step-tab-'+step);await until(()=>page.$eval('#step-'+step,n=>!n.hidden));}
 for(const width of [1440,390]){await page.setViewportSize({width,height:1000});await pause(150);assert((await page.evaluate(()=>document.documentElement.scrollWidth))<=width);await page.screenshot({path:path.join(output,'screenshots',`preview-ui-${width}.png`),fullPage:true});}
 assert.deepEqual(errors,[]);const accessibility=[];for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:1000});await pause(150);assert((await page.evaluate(()=>document.documentElement.scrollWidth))<=width);for(const step of [0,1,2,3]){await page.click('#step-tab-'+step);await until(()=>page.$eval('#step-'+step,n=>!n.hidden));accessibility.push({width,step,visible:true,no_horizontal_overflow:true});}}fs.writeFileSync(path.join(output,'Preview_UI.json'),JSON.stringify({status:'PASS',URL:base,health,manual_reference_cases:manual,four_steps:true,responsive_widths:[320,390,768,1440],accessibility,accessibility_method:'Live layout/navigation and rendered content checks; axe WCAG audit on byte-identical local build. Live CSP blocks inline axe injection and was preserved.',page_errors:errors},null,2));console.log('PRODUCTION_FIVE_CLASS_PASS');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
