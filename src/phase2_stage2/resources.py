"""Fixed-thread, warm single-observation end-to-end validation latency protocol."""
import time,pickle,warnings
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from .contracts import *


def protocol():
 result=runtime();result.update({'warmups':WARMUPS,'timed_single_observations':TIMED_CALLS,
  'sample_seed':SEED,'sample_population':'validation block 13; seeded uniform positions with replacement; same positions for every model/configuration',
  'scope':'Complete wrapper prediction: schema/availability checks, quality handling, imputation, derivative construction, scaling where applicable, and classifier.',
  'excluded':'CSV I/O and construction of input DataFrame; one-row frames are prepared outside timed regions.',
  'batch_size':1,'threadpool_limit':2,'estimator_threads':'Frozen Stage 1 settings: RF and LightGBM n_jobs=2.',
  'clock':'time.perf_counter_ns','quantile_method':'numpy.percentile linear interpolation',
  'abstention_state':'Independent single-row calls reset positional availability state; reference rows have no unavailable values.',
  'artifact':'Uncompressed pickle protocol 5 of complete fitted wrapper/pipeline; excludes installed dependencies and environment.'})
 return result


def measure(model,X):
 rng=np.random.default_rng(SEED);indices=rng.integers(0,len(X),size=WARMUPS+TIMED_CALLS)
 frames=[X.iloc[[int(i)]] for i in indices]
 with threadpool_limits(2),warnings.catch_warnings():
  warnings.filterwarnings('ignore',message=r'`sklearn.utils.parallel.delayed` should be used.*',category=UserWarning)
  for sample in frames[:WARMUPS]:model.predict_proba(sample)
  durations=[]
  for sample in frames[WARMUPS:]:
   start=time.perf_counter_ns();model.predict_proba(sample);durations.append((time.perf_counter_ns()-start)/1e6)
  pools=threadpool_info()
 a=np.array(durations)
 return {'p50_ms':float(np.percentile(a,50)),'p95_ms':float(np.percentile(a,95)),
  'p99_ms':float(np.percentile(a,99)),'mean_ms':float(a.mean()),'min_ms':float(a.min()),'max_ms':float(a.max()),
  'timed_calls':len(durations),'warmups':WARMUPS,'latency_samples_ms':durations,'threadpools':pools,
  'sample_position_digest':index_digest(X.index.to_numpy()[indices[WARMUPS:]])}
