# PatchGym Ingestion

SandboxLedger can append a PatchGym run directory to a tamper-evident ledger:

```bash
sandboxledger ingest-patchgym ledger.jsonl .patchgym/runs/latest
sandboxledger verify ledger.jsonl
```

The ingestion command reads `manifest.json` and records digests for:

- `manifest.json`;
- `trace.jsonl`;
- `report.json`;
- `report.md`;
- `index.html` when present;
- per-task artifacts declared by the PatchGym manifest, such as agent patch,
  stdout, stderr, and validation output.

The ledger record metadata includes the PatchGym schema version, agent label,
task count, solved count, failed count, and run directory.

## Boundary

SandboxLedger records what files existed and what their hashes were when the
record was appended. It does not sandbox execution. Pair it with PatchGym's run
artifacts and a disposable container or VM when running untrusted agents.

