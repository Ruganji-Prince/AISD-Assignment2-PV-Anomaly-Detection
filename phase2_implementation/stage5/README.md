# Publication verification

The approved report and all scientific experiment records are frozen. The root README contains the authorized append-only Phase 2 section, following the current remote Phase 1 text. Historical Phase 1/experiment hash manifests remain unedited; the README publication exception is recorded separately in `Publication_Exceptions.json`.

From the repository root, with the frozen Phase 2 review dependencies installed:

```powershell
python -B phase2_implementation/verify_submission.py
```

This entry point checks the exact current inclusion manifest, frozen scientific hashes, README prefix preservation, paths, credentials and large files. It then runs the unchanged Stage 4 evidence verifier in an isolated temporary copy containing only public files. Neither Git metadata nor model caches are required. Temporary copying and cleanup occur under ignored `.cache/publication-review/`; verification does not train, tune, generate predictions or regenerate the approved report/figures.

The canonical current publication manifest is `phase2_implementation/stage4/evidence/Publication_File_Hashes.json`. Updating this packaging manifest does not rewrite any scientific evidence. The previous reviewed packaging manifest is preserved locally; original scientific values and report-to-evidence mappings remain unchanged. `Scientific_Protection.json` records the approved scientific/public source hashes carried forward without modification.

Full experimental training reproduction remains distinct from this evidence-only check, as documented in the Phase 2 reproduction guide. Original local-only checkpoints, trained models, prediction arrays, SHAP arrays, environments and redundant diagnostics are intentionally excluded from publication and preserved locally.
