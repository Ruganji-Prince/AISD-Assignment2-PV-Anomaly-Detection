const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = (process.env.PV_APP_URL || 'http://127.0.0.1:8765').replace(/\/$/, '');
const screenshots = process.env.PV_SCREENSHOT_DIR;
(async () => {
 const browser = await chromium.launch({headless:true,args:base.startsWith('http://127.0.0.1')?['--no-proxy-server']:[]});
 const page = await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 let response=await page.goto(base, {waitUntil:'domcontentloaded'});assert.equal(response.status(),200);
 await page.locator('#service-status').filter({hasText:'Model ready'}).waitFor({timeout:60000});
 assert.equal(await page.locator('h1').textContent(),'PV Anomaly Detection.');
 await page.locator('#example-select option').nth(5).waitFor({state:'attached'});
 const examples=await (await page.request.get(base+'/api/examples')).json();
 for (let k=0;k<5;k++) {
  await page.selectOption('#example-select',String(k));await page.click('#load-example');
  const example=examples.find(x=>x.id===k);
  for (const [key,value] of Object.entries(example.measurements)) assert.equal(Number(await page.inputValue('#'+key)),value);
  const pending=page.waitForResponse(r=>r.url().endsWith('/api/predict')&&r.request().method()==='POST');
  await page.click('#predict-button');const prediction=await pending;
  assert.equal(prediction.status(),200);const data=await prediction.json();assert.equal(data.predicted_class,k);
  await page.waitForFunction(k=>document.getElementById('predicted-class').textContent===String(k)&&!document.getElementById('result-content').hidden,k);
  assert.equal(await page.getAttribute('#result-card','data-category'), k===0?'normal':k===4?'environmental_condition':'hardware_fault');
 }
 assert.match(await page.locator('#category-badge').textContent(),/not hardware failure/);
 if(screenshots){fs.mkdirSync(screenshots,{recursive:true});await page.screenshot({path:path.join(screenshots,'desktop.png'),fullPage:true});}
 await page.click('#reset-button');
 assert.equal(await page.inputValue('#vdc1'),'');assert.equal(await page.locator('#result-content').isVisible(),false);
 let calls=0;const watch=r=>{if(r.url().endsWith('/api/predict')&&r.method()==='POST')calls++;};page.on('request',watch);
 await page.fill('#vdc1','-1');await page.fill('#vdc2','300');await page.fill('#idc1','1');await page.fill('#idc2','1');await page.click('#predict-button');
 assert.equal(await page.$eval('#vdc1',e=>e.validity.rangeUnderflow),true);assert.equal(calls,0);page.off('request',watch);
 await page.selectOption('#example-select','0');await page.click('#load-example');
 await page.route('**/api/predict',async route=>{await new Promise(resolve=>setTimeout(resolve,350));await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'The prediction service is unavailable. Please try again later.'})});});
 await page.click('#predict-button');await page.locator('#loading-spinner').waitFor({state:'visible'});assert.equal(await page.isDisabled('#predict-button'),true);
 await page.locator('#form-error').waitFor({state:'visible'});assert.match(await page.locator('#form-error').textContent(),/unavailable/);assert.equal(await page.locator('#result-content').isVisible(),false);await page.unroute('**/api/predict');
 for (const width of [390,320]) {
  await page.setViewportSize({width,height:844});await page.reload({waitUntil:'domcontentloaded'});
  await page.selectOption('#example-select','4');await page.click('#load-example');await page.click('#predict-button');await page.locator('#predicted-label').filter({hasText:'Natural Building Shade'}).waitFor({timeout:60000});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false,'horizontal overflow at '+width);
  if(screenshots)await page.screenshot({path:path.join(screenshots,'mobile-'+width+'.png'),fullPage:true});
 }
 assert.deepEqual(errors,[]);
 await browser.close();console.log(JSON.stringify({status:'PASS',url:base,real_classes_tested:[0,1,2,3,4],desktop:1440,mobile_widths:[390,320],reset:true,loading:true,api_error_display:true,invalid_input_blocked:true,page_errors:errors},null,2));
})().catch(error=>{console.error(error);process.exit(1);});
