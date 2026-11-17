'use strict';
const $ = id => document.getElementById(id);
const channels = ['vdc1', 'vdc2', 'idc1', 'idc2'];
const descriptions = {
  0: 'The supplied measurements are classified as normal operation.',
  1: 'The supplied measurements show a pattern associated with a short-circuit fault. Qualified electrical inspection is needed to establish the actual condition.',
  2: 'The supplied measurements show a pattern associated with resistive degradation. Qualified electrical inspection is needed to establish the actual condition.',
  3: 'The supplied measurements show a pattern associated with an open-circuit fault. Qualified electrical inspection is needed to establish the actual condition.',
  4: 'The supplied measurements are classified as natural building shade. This is an environmental condition, not a hardware-failure class.'
};
const labels = ['Normal', 'Short Circuit', 'Resistive Degradation', 'Open Circuit', 'Natural Building Shade'];
let examples = [];
let busy = false;
let controller;
function showError(message) { $('form-error').textContent = message; $('form-error').hidden = false; }
function clearError() { $('form-error').hidden = true; $('form-error').textContent = ''; }
function setBusy(value) {
  busy = value;
  $('predict-button').disabled = value;
  $('reset-button').disabled = value;
  $('load-example').disabled = value || $('example-select').value === '';
  $('loading-spinner').hidden = !value;
  $('button-icon').hidden = value;
  $('button-label').textContent = value ? 'Analyzing measurements...' : 'Predict operating condition';
  $('result-card').setAttribute('aria-busy', String(value));
}
function clearResult() {
  $('result-content').hidden = true;
  $('result-empty').hidden = false;
  $('result-warnings').hidden = true;
  delete $('result-card').dataset.category;
}
function renderResult(result) {
  if (!Number.isInteger(result.predicted_class) || !labels[result.predicted_class] || !['normal','hardware_fault','environmental_condition'].includes(result.fault_category)) throw new Error('The service returned an invalid response. Please try again.');
  const k = result.predicted_class;
  $('result-card').dataset.category = result.fault_category;
  $('category-badge').textContent = k === 0 ? 'Normal operating state' : k === 4 ? 'Environmental condition - not hardware failure' : 'Hardware-fault class';
  $('result-symbol').textContent = k === 0 ? '\u2713' : k === 4 ? '\u2601' : '!';
  $('predicted-label').textContent = labels[k];
  $('predicted-class').textContent = String(k);
  $('result-description').textContent = descriptions[k];
  $('result-warnings').textContent = (result.warnings || []).join(' ');
  $('result-warnings').hidden = !(result.warnings || []).length;
  $('result-empty').hidden = true;
  $('result-content').hidden = false;
  $('predicted-label').setAttribute('tabindex', '-1');
  $('predicted-label').focus({preventScroll: true});
  if (window.matchMedia('(max-width:700px)').matches) $('result-card').scrollIntoView({behavior:'smooth',block:'start'});
}
$('prediction-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (busy) return;
  clearError();
  const measurements = {};
  for (const name of channels) {
    const raw = $(name).value.trim();
    const value = Number(raw);
    if (raw === '' || !Number.isFinite(value) || value < 0) { showError('Enter a finite, nonnegative number in all four fields.'); $(name).focus(); return; }
    measurements[name] = value;
  }
  clearResult();
  setBusy(true);
  controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch('/api/predict', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(measurements), signal:controller.signal});
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'The prediction service could not process these measurements.');
    renderResult(result);
  } catch (error) {
    showError(error.name === 'AbortError' ? 'The request timed out. Please try again.' : error instanceof TypeError ? 'Unable to reach the prediction service. Check the connection and try again.' : error.message);
  } finally { clearTimeout(timer); setBusy(false); }
});
$('prediction-form').addEventListener('reset', () => { clearError(); clearResult(); $('example-select').value = ''; $('load-example').disabled = true; $('example-status').textContent = 'Measurements cleared.'; });
$('example-select').addEventListener('change', () => { $('load-example').disabled = busy || $('example-select').value === ''; });
$('load-example').addEventListener('click', () => {
  const example = examples.find(x => String(x.id) === $('example-select').value);
  if (!example || busy) return;
  for (const name of channels) $(name).value = example.measurements[name];
  clearError(); clearResult();
  $('example-status').textContent = 'Dataset measurements loaded. Select Predict operating condition to analyze.';
});
async function initialize() {
  try {
    const response = await fetch('/api/examples');
    if (!response.ok) throw new Error();
    examples = await response.json();
    for (const example of examples) {
      const option = document.createElement('option'); option.value = example.id; option.textContent = labels[example.id] + ' sample'; $('example-select').append(option);
    }
  } catch { $('example-select').disabled = true; $('example-status').classList.remove('sr-only'); $('example-status').textContent = 'Examples are temporarily unavailable. Measurements can still be entered manually.'; }
  try {
    const response = await fetch('/api/health');
    if (!response.ok) throw new Error();
    $('service-status').lastChild.textContent = 'Model ready';
  } catch {
    $('service-status').lastChild.textContent = 'Service unavailable';
    $('service-status').classList.add('unavailable');
  }
}
initialize();
