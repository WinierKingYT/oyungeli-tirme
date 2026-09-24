# Release Management

An RC requires:

- reproducible versioned build;
- P0 = 0 and P1 = 0;
- critical E2E scenarios green;
- performance/memory/network budgets green;
- save migration and corruption handling green;
- multiplayer soak green where applicable;
- target-platform checks green;
- content reference validation green;
- known limitations and rollback plan;
- independent RC disposition.

No agent may publish, deploy, tag, or push a release without explicit human authorization.

