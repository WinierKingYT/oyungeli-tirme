# Build and CI Standard

CI should reproduce clean checkout validation: configuration/schema checks, compile/build, automated tests, content/reference validation, packaging smoke, and artifact metadata. Platform-specific gates run where required.

Required properties:

- pinned engine/toolchain and dependency versions;
- no reliance on untracked local state;
- immutable revision and artifact identity;
- clear separation of pre-existing failures and new regressions;
- retained logs/reports for acceptance;
- branch protection for required gates;
- no secret values in logs or repository files.

Exact workflows remain `TBD` until project discovery.

