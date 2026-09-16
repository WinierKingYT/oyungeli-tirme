# Failure Injection Catalog

Candidate injections:

- 300 ms latency and 5% packet loss;
- player disconnect/reconnect during interaction;
- save write failure or truncated save;
- missing asset/reference/configuration;
- destroyed or orphaned cargo;
- engine at critical heat with limited repair resources;
- island service unavailable;
- inventory/economy request duplicated or reordered;
- invalid network authority request;
- level transition interruption.

Every injection defines the expected controlled failure, observability signal, recovery, invariant, and prohibited outcome.

