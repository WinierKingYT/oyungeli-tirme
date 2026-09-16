# Evidence Registry

Evidence packs live here under stable IDs such as `EVID-TASK-CARGO-001-R1/`.

An evidence pack contains:

- manifest with task/system/revision/environment;
- acceptance-criteria matrix;
- exact commands and outcomes;
- logs, reports, screenshots, captures, profiler data, or replay references;
- deviations, pre-existing failures, limitations, and unresolved risk;
- reviewer identity, date, and disposition.

Evidence is immutable after acceptance. Corrections create a new revision and retain the prior record.

Use `python scripts/artifact_digest.py <evidence-pack>` to produce the deterministic digest stored in the independent acceptance receipt.

Keep the acceptance receipt beside, not inside, the hashed evidence-pack directory. Otherwise the receipt would change the digest it is intended to record.
