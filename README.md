# SandboxLedger

SandboxLedger records benchmark and agent runs as an
append-only, content-addressed JSONL ledger. Each record hashes
its command, metadata, outputs, artifact digests, and previous
record hash; the ledger exposes a Merkle root for quick
integrity checks.

It is not a sandbox by itself. It is the reproducibility layer
that a sandboxed runner, coding-agent benchmark, or RAG eval
can use to prove what was run and whether the record was
modified later.

## Install

```bash
git clone https://github.com/nripankadas07/sandboxledger
cd sandboxledger
python -m pip install -e .
```

## Quick Start

```bash
sandboxledger record ledger.jsonl --command "pytest -q" --status pass
sandboxledger verify ledger.jsonl
sandboxledger ingest-patchgym ledger.jsonl .patchgym/runs/latest
```

## Guarantees

- deterministic canonical JSON hashing
- previous-hash chain checks
- artifact SHA-256 capture
- Merkle root summary
- tamper detection for edited records
- PatchGym run ingestion for `manifest.json`, `trace.jsonl`, reports, and
  per-task agent artifacts

See [PatchGym ingestion](docs/patchgym-ingest.md) for the run-ledger flow.

## Development

```bash
python -m unittest discover -s tests -v
```
