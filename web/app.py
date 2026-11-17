"""FastAPI adapter around the unchanged, hash-verified original inference CLI."""
import json
import logging
import sys
from functools import lru_cache
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from src.inference.cli import ROOT, SHA256, load_model, predict, validate

STATIC = Path(__file__).parent / 'static'
app = FastAPI(title='PV Anomaly Detection', docs_url=None, redoc_url=None, openapi_url=None)
app.mount('/assets', StaticFiles(directory=STATIC), name='assets')
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def fitted_model():
    return load_model()

def inference(record):
    result = predict(record, fitted_model())
    category = 'environmental_condition' if result['environmental_shade'] else ('hardware_fault' if result['hardware_fault_class'] else 'normal')
    result['fault_category'] = category
    result['warnings'] = [f'{name} is outside the observed training range. This is not a certified operating limit.' for name in result['range_warnings']]
    return result

@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

@app.get('/', include_in_schema=False)
def homepage():
    return FileResponse(STATIC / 'index.html')

@app.get('/api/health')
async def health():
    try:
        await run_in_threadpool(fitted_model)
    except Exception:
        logger.error('Original fitted model failed readiness verification.')
        return JSONResponse({'status': 'unavailable', 'message': 'Model verification failed. Predictions are unavailable.'}, status_code=503)
    return {'status': 'ready', 'model_sha256': SHA256, 'python_version': '.'.join(map(str, sys.version_info[:3]))}

@app.get('/api/examples')
def examples():
    cases=json.loads((ROOT/'deployment/example_cases.json').read_text(encoding='utf8'))
    return [{'id': c['case'], 'name': c['output']['label'], 'measurements': c['input']} for c in cases]

def reject_constant(value):
    raise ValueError('Nonfinite values are not accepted.')

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError('Duplicate input fields are not accepted.')
        result[key]=value
    return result

@app.post('/api/predict')
async def predict_measurements(request: Request):
    if request.headers.get('content-type','').split(';')[0].strip().lower() != 'application/json':
        raise HTTPException(415, 'Send the four measurements as application/json.')
    body=bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body)>2048: raise HTTPException(413, 'Input is too large. Send one set of four measurements.')
    try:
        record=json.loads(body, parse_constant=reject_constant, object_pairs_hook=unique_object)
        validate(record)
    except (ValueError, TypeError, UnicodeDecodeError, RecursionError) as exc:
        raise HTTPException(422, 'Enter exactly four finite, nonnegative numbers: vdc1, vdc2 (V), idc1, idc2 (A). No additional fields are accepted.') from exc
    try:
        await run_in_threadpool(fitted_model)
    except Exception:
        logger.error('Original model verification unavailable; no prediction returned.')
        raise HTTPException(503, 'The prediction service is unavailable. Please try again later.')
    try:
        return await run_in_threadpool(inference, record)
    except (ValueError, OverflowError):
        raise HTTPException(422, 'These measurements exceed the supported numeric range. Check the values and units.')
    except Exception:
        logger.error('Original model inference unavailable; no prediction returned.')
        raise HTTPException(503, 'The prediction service is unavailable. Please try again later.')
