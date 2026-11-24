# Live demonstration checklist

Preparation should finish before the evaluation; do not fit21 models or regenerate the notebook during the live demonstration.

1. Open the public repository and [current report](../refinement/Final_Report.md). Show the full commit SHA and protected model hash.
2. Run the quick verification in the prepared environment. Confirm30 tests and protected-byte checks pass. Keep a terminal with the output.
3. Open the four-step application. Confirm a single active step, keyboard navigation and responsive layout.
4. Use historical dataset examples to demonstrate all five actual model classes. Explain shade as environmental. Show missing/negative inputs are rejected and out-of-range values warned rather than silently clipped.
5. Explain that original synthetic presets remain illustrative and can disagree. Run the predetermined TRAIN-derived CLI demo; display conditioning label and actual prediction separately, without searching for a matching example.
6. Show the frozen bounds, separator count and class-support table. Explain why grouped validation cannot learn class 1 when block 12 is withheld.
7. Show no exact feature overlaps, full near-neighbor counts and their limits. Similar operating states are not automatically target leakage.
8. Show the original model comparison, reproduced calibration and uncertainty sensitivity. Confirm calibration/threshold policy is not deployed in the classifier API.
9. Show actual Linux matrix evidence and the server/network timing table. State the unchanged10ms/10MiB targets and resource failures clearly.
10. Close with known limitations and concrete next deployment requirements. No slide presentation or new scientific claims are needed.

Before the session: confirm internet access and public health readiness once. A readiness call may initialize the model, so subsequent calls are warm; do not call the next request a cold start. If a cold request times out, report the error, retry readiness once and use the preserved successful evidence. Repeatedly redeploying to manufacture cold starts is prohibited.

A distributed per-user rate limiter is not deployed. The tested local capacity guard and response deadlines are narrower safeguards. No cloud purchase or provider firewall change is needed for this demonstration.
