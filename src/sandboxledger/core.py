from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union
import hashlib
import json


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def hash_record(record: Mapping[str, Any]) -> str:
    body = {key: value for key, value in record.items() if key != "record_hash"}
    return sha256_bytes(canonical_json(body))


def artifact_digest(path: Union[str, Path]) -> Dict[str, Any]:
    p = Path(path)
    data = p.read_bytes()
    return {"path": str(p), "bytes": len(data), "sha256": sha256_bytes(data)}


def create_record(
    command: str,
    status: str,
    artifacts: Optional[Sequence[Union[str, Path]]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    stdout: str = "",
    stderr: str = "",
) -> Dict[str, Any]:
    artifact_rows = [artifact_digest(path) for path in (artifacts or [])]
    return {
        "schema_version": "sandboxledger.v1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "command": command,
        "status": status,
        "metadata": dict(metadata or {}),
        "artifacts": artifact_rows,
        "outputs": {
            "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
            "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        },
    }


def read_ledger(path: Union[str, Path]) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    rows = []
    for line_no, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def append_record(path: Union[str, Path], record: Mapping[str, Any]) -> Dict[str, Any]:
    p = Path(path)
    records = read_ledger(p)
    materialized = dict(record)
    materialized["previous_hash"] = records[-1]["record_hash"] if records else None
    materialized["record_hash"] = hash_record(materialized)
    with p.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(materialized, sort_keys=True) + "\n")
    return materialized


def merkle_root(records: Sequence[Mapping[str, Any]]) -> str:
    level = [str(record["record_hash"]) for record in records]
    if not level:
        return sha256_bytes(b"")
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [sha256_bytes((level[i] + level[i + 1]).encode("ascii")) for i in range(0, len(level), 2)]
    return level[0]


def verify_records(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    errors: List[str] = []
    previous = None
    for index, record in enumerate(records):
        expected_hash = hash_record(record)
        if record.get("record_hash") != expected_hash:
            errors.append(f"record {index}: hash mismatch")
        if record.get("previous_hash") != previous:
            errors.append(f"record {index}: previous_hash mismatch")
        previous = record.get("record_hash")
    return {"valid": not errors, "records": len(records), "merkle_root": merkle_root(records), "errors": errors}


def verify_ledger(path: Union[str, Path]) -> Dict[str, Any]:
    return verify_records(read_ledger(path))
