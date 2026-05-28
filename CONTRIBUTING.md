# Contributing

SandboxLedger is a content-addressed reproducibility ledger for local benchmark
and agent runs. Contributions should strengthen determinism, auditability, or
tamper detection.

Before opening a pull request:

- run `python -m unittest discover -s tests -v`;
- add a ledger fixture for format or verification changes;
- preserve canonical JSON hashing compatibility unless the schema changes;
- document any schema change in `CHANGELOG.md`.

