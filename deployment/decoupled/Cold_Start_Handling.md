# Bounded cloud startup and failure handling

The earlier Azure milestone observed56.94seconds for one prediction after confirmed zero replicas. That is not a guaranteed maximum. This revision retains min0/max1 and adds demand-driven readiness rather than always-on capacity or background warming.

- Page initialization starts one shared readiness attempt and displays Connecting.
- After1.5seconds of waiting, the interface displays Starting cloud inference service and explains that approximately one minute may be needed.
- Each health request is bounded to30seconds including body reading; transient failures can retry after two seconds only within the overall120-second attempt.
- A verified ready response must contain the original model SHA. Readiness polling stops immediately when ready, or at the bounded attempt limit with Unavailable and Retry connection.
- Successful readiness is cached for at most30seconds. A later user prediction can recheck health on demand, accommodating an idle tab and Azure scale-to-zero. No interval or continuous keepalive is scheduled.
- The normal prediction request retains a distinct60-second client deadline. Backend body/inference deadlines remain5/15seconds.
- One shared pending readiness promise and the existing busy guard prevent duplicate startup/prediction submissions. The retry button is re-enabled after failures.
- Network/timeout failures clear prediction presentation and return a controlled error. No fabricated or cached substitute prediction is displayed.

[Browser evidence](Browser_Network_Verification.json) includes delayed real health checks, a320px startup layout check, duplicate submission, blocked-Azure/no-fallback behavior and retry recovery. Bounded startup and inference timeout tests use intercepted browser requests and a virtual clock. They are explicitly simulated failure tests, not measurements of a new physical cold start. Azure was not shut down or force-scaled for these tests.

The warm browser readiness observation and API latency are in [timing evidence](Latency_Summary.json). They must not be substituted for cold-start timing. Startup can still exceed120seconds under service/network failure; the interface then offers an explicit retry. No startup SLA, cloud production readiness or safety-monitoring reliability is claimed.
