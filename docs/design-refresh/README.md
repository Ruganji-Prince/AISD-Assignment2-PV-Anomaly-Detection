# PV frontend design review

Status: implementation and local Azure-backed verification complete. Public design preview is blocked by the existing exact-origin CORS allowlist; production and main are unchanged by this branch.

## Starting point and design audit

The branch `design/pv-frontend-refresh` starts from the latest main at the full revision recorded in [publication safety](Publication_Safety.json). The [original inventory](Content_Baseline.json) records all 77 IDs, 35 controls, 113 text nodes and source hashes before editing. Existing content is a four-step workflow: measurements, scenarios, graphical analysis and assessment. The existing frontend has no evaluation-metric table or confusion-matrix image; those scientific deliverables remain in the repository. No substitute figures or metrics were invented.

The original implementation used very small labels, a fixed desktop-height assumption and accumulated CSS overrides. The redesign uses a compact editorial hero, original inline solar/cloud SVG, navy/yellow actions, an accessible sticky header, a readable horizontal desktop/two-column mobile stepper, larger inputs, scenario-selection cards, larger chart labels and distinct result/limitations sections. Existing controls remain available. All added navigation links target actual page sections. Scenario cards dispatch the existing selector change event and preserve synthetic/reference distinctions. They do not compute predictions.

No SEforALL HTML file was available among the provided attachments or the attachment HTML search. The supplied palette/layout brief informed an original implementation; no claim is made that the missing reference source was reviewed. No external branding, imagery, tracking, fonts, framework or runtime dependency was added.

## Visual system

| Token | Use |
| --- | --- |
| Navy `#003E66` | Hero, sticky header, selected step, primary headings |
| Ocean `#087E99` | Graphics and controls |
| Ocean text `#066B83` | Small text on tinted surfaces; contrast correction |
| Solar `#FFB800` | Main actions and original solar illustration |
| Soft blue `#F3F9FC` | Page and analytical callouts |
| Ink `#102B3F` | Body text |
| Green / red / amber | Normal / hardware fault / environmental shade, always accompanied by labels |

System fonts, 16px base text, fluid headings, shared spacing/radius/state tokens and at least 44px main controls replace the earlier small type. Dark text is used on yellow actions. Reduced-motion styling and visible keyboard focus remain supported. Only the hidden-attribute utility and reduced-motion rules use necessary `!important` declarations.

## Before and after screenshots

[Before contact sheet](screenshots/before-contact-sheet.jpg) | [After contact sheet](screenshots/after-contact-sheet.jpg) | [New landing](screenshots/after/landing.png)

All 24 before and 24 after full-page screenshots are in the corresponding folders: six widths (375, 430, 768, 1024, 1440, 1920) times all four steps. The contact sheets show analytical portions for comparison; full-page originals retain the landing/header. [Before checks](before-visual-results.json) and [after checks](after-visual-results.json) record geometry. Screenshot review found no horizontal overflow, lost panels or clipped form/chart labels. Desktop pages deliberately scroll vertically so readable content is not forced into one screen.

## Preservation checklist

| Existing content or behavior | Verification |
| --- | --- |
| All original static words and element IDs | 113 text nodes and 77 IDs retained, [automated preservation](Preservation_And_Tests.json) |
| Four inputs, units, validation, submit, reset | Existing functional regression passed |
| Synthetic/reference selectors and all five examples | Existing regression plus new card/selector checks passed |
| Charts, tooltips, axes, legends and intent schematic | Existing regression and all six-width screenshots passed |
| Result class, explanations, warnings, environmental shade | Original rendering and explanation source preserved; five-class parity passed |
| Loading, readiness, retries, bounded deadlines, duplicate prevention | Unchanged API module plus live browser tests passed |
| Navigation, keyboard, source retention and no reload | Existing functional checks passed |
| Original model, scientific results, approved PDF and protected tag | Files unchanged; publication safety check |
| Azure transport, API contract, CSP, CORS and build safeguard | Byte-identical transport/build/backend configuration; read-only cloud check |

[45 unit tests](Preservation_And_Tests.json) passed. [Existing browser regression](Functional_Regression.json) passed with one explicit adaptation: its old no-desktop-vertical-scroll assertion is retired for the new landing/readable layout. Original test files were not edited. All functional assertions remain; horizontal overflow is still forbidden.

[Live browser evidence](cloud-evidence/Browser_Network_Verification.json) verifies all five actual Azure predictions (0, 1, 2, 3, 4), correct displayed explanations, direct cross-origin requests, duplicate prevention, retry recovery, no local fallback and no background keepalive. Timeout/failure tests use browser interception and a virtual clock, not an Azure shutdown. Five historical reference observations establish deployment parity, not fresh accuracy. Synthetic intents still can predict another class, including class 4; no generator or model changes were made.

[Accessibility results](Accessibility_Results.json): axe-core 4.14.1 reported zero A/AA violations across three widths and four steps. Keyboard arrows/Home/End, visible focus and new scenario-card behavior passed. Some automated checks remain marked incomplete and require manual review; this is not a full screen-reader or WCAG certification. The temporary axe script is ignored local test tooling and is absent from deployed assets.

[Performance comparison](Performance_Comparison.json): served assets increased from 62,634 to 65,206 bytes, with the same nine output files, zero runtime dependencies, model artifacts, Python files or functions. Fifteen warm browser-to-Azure requests succeeded; measured p95 was 227.50ms. This small local sample does not establish a causal speedup, production TTFB improvement or cold-start reliability. Original 10ms/10MiB targets remain unchanged and unmet.

## Review and reproduction

Use the existing Python environment documented in the project. From the repository root:

```sh
python -m frontend.build --output .review/design/.vercel/output --manifest .review/design-manifest.json
python -m http.server 8080 --bind 127.0.0.1 --directory .review/design/.vercel/output/static
```

Open http://127.0.0.1:8080. The static page calls the real Azure API using the already-permitted local origin. Use a fresh output directory; no local backend is required. Existing bounded startup may take time. Do not package review screenshots or tooling into the static output.

With the existing Playwright installation available through NODE_PATH, run `node docs/design-refresh/visual-check.cjs after`. The accessibility harness expects the published axe-core test script at ignored `.review/axe.min.js`; obtain it from the npm package, never add it to the frontend runtime. Set PV_NODE to the Node executable and PV_APP_URL to localhost8080, then run `python docs/design-refresh/functional-check.py` for the documented legacy test adapter. The original `deployment/decoupled/browser_verify.cjs` can write fresh evidence to an external directory selected by PV_EVIDENCE_DIR.

## Preview restriction and safe release plan

The existing Azure allowlist contains only the two production aliases, the old immutable preview hostname, localhost8080 and 127.0.0.1:8080. A new design preview hostname is not covered; the old generated deployment hostname cannot be repurposed as a mutable new deployment. No new Vercel preview was created and no CORS setting was changed. The [static build inventory](Static_Build_Manifest.json) is verified locally; no remote design-output inspection can be claimed yet.

1. Review the branch and screenshots locally. Obtain separate approval for one dedicated exact design-review origin in Azure CORS before creating a shared preview. Do not broaden to wildcards or reuse a production alias.
2. If authorized, keep the same app/image/resources and add only that origin. Manually deploy the static prebuilt output to the existing Vercel project and approved review alias. Retain the fail-closed Git/source-build safeguard.
3. Verify actual preview outputs, canonical API base, CSP, five-class parity, browser failures and responsive layout at the shared URL.
4. Obtain separate production-promotion and main-integration approval. Vercel preview promotion can create a new production deployment ID; verify asset identity rather than assuming ID retention. Use staged production output where supported.
5. After approval, retain the current production deployment and roll back with `vercel rollback <preserved-production-url> --yes --scope prince-r-k` if release checks fail. Never use retraining, changed scientific files, force push or history rewriting as part of a visual release.

Production, Azure, main, the existing model and the protected submission tag are outside this design commit. Existing academic results and previously recorded TEST limitations remain unchanged.
