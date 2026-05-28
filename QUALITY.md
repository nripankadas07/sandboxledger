# Quality Notes

SandboxLedger should make run records tamper-evident and easy to verify.

Current gates:

- unit tests for hash-chain verification and tamper detection;
- CLI regression tests for record and verify commands;
- Python 3.9 and 3.13 CI;
- no hidden state outside the JSONL ledger and declared artifacts.

Schema changes should be additive where possible and must keep verification
errors specific enough to debug.

