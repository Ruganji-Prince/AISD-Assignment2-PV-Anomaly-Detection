# Browser-origin serving measurements

The [raw 15-request benchmark](Latency_Benchmark.csv) and [summary](Latency_Summary.json) were measured from the verified browser preview to the actual Azure API. All 15 sequential warm requests succeeded with the expected original-model result.

| Component | p50 ms | p95 ms | p99 ms |
| --- | ---: | ---: | ---: |
| Browser API round trip | 179.00 | 263.00 | 291.00 |
| Server including validation | 13.92 | 17.07 | 20.32 |
| Fitted preprocessing | 5.38 | 7.62 | 9.96 |
| Random Forest | 6.33 | 7.74 | 8.50 |

Page loadEventEnd was 4205.7 ms, including DNS and connection establishment. Readiness transitioned from Connecting at 4204.0 ms to Ready at 4708.8 ms: 504.8 ms of warm readiness. Five-case submit-to-DOM durations were 308.2, 309.4, 342.6, 429.6 and 298.9 ms. These include API/JSON/DOM handling and do not isolate GPU paint or browser rendering time.

The earlier matched httpx Azure/Vercel experiment reported network p95 248.99/448.21 ms and server p95 16.62/16.71 ms. Those historical records remain unchanged. Different clients, protocols and measurement times prevent attributing differences to decoupling or model improvement. Fifteen sequential observations do not estimate sustained concurrency, an SLA or stable tail quantiles.

A previous naturally observed zero-replica access took 56.94 seconds. This extension tested delayed health, a simulated 121-second startup deadline and a simulated 61-second prediction deadline without shutting down Azure or changing scaling. No new physical cold-start guarantee is established. Existing 10 ms complete-path and 10 MiB model targets remain unmet; the original model is 12,232,020 bytes. Resource limits and cost exposure are unchanged; no new cost estimate replaces the [existing analysis](../azure/Cost_Analysis.md).
