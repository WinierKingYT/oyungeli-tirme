# Documentation Authority

Each authoritative artifact has one owner, stable ID, lifecycle state, revision, and evidence links. Duplicated summaries are non-authoritative unless an index explicitly says otherwise.

## Required labels

- `FACT`: directly inspected or measured.
- `DECISION`: explicitly approved choice.
- `HYPOTHESIS`: testable belief not yet validated.
- `PROPOSAL`: candidate not yet authoritative.
- `UNKNOWN`: missing material information.
- `DEPRECATED`: retained for history, not current truth.

## Drift rule

When code, asset, configuration, documentation, or evidence disagree, record both sides and stop the affected acceptance claim. Do not silently edit history to make them appear consistent.

## Versioning

Accepted documents record the immutable repository revision they describe. Later edits either create a new version or explicitly invalidate the old acceptance record.

