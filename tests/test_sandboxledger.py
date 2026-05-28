from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
import io
import json
import unittest

from sandboxledger import append_patchgym_run, append_record, create_record, verify_ledger
from sandboxledger.cli import main


class SandboxLedgerTests(unittest.TestCase):
    def test_chain_verifies_and_tamper_is_detected(self):
        with TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            append_record(ledger, create_record("pytest -q", "pass"))
            append_record(ledger, create_record("ruff check .", "pass"))
            self.assertTrue(verify_ledger(ledger)["valid"])
            rows = ledger.read_text(encoding="utf-8").splitlines()
            first = json.loads(rows[0])
            first["status"] = "failed"
            rows[0] = json.dumps(first, sort_keys=True)
            ledger.write_text("\n".join(rows) + "\n", encoding="utf-8")
            result = verify_ledger(ledger)
            self.assertFalse(result["valid"])
            self.assertIn("hash mismatch", " ".join(result["errors"]))

    def test_cli_record_and_verify(self):
        with TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.assertEqual(main(["record", str(ledger), "--command", "pytest -q", "--status", "pass"]), 0)
                self.assertEqual(main(["verify", str(ledger)]), 0)

    def test_patchgym_run_can_be_ingested(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            task_dir = run_dir / "task-1"
            task_dir.mkdir(parents=True)
            (run_dir / "report.json").write_text('{"agent":"oracle","results":[]}\n', encoding="utf-8")
            (run_dir / "trace.jsonl").write_text('{"actor":"patchgym"}\n', encoding="utf-8")
            (task_dir / "agent.patch").write_text("diff --git a/a b/a\n", encoding="utf-8")
            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "patchgym.run_manifest.v1",
                        "agent": "oracle",
                        "totals": {"tasks": 1, "solved": 1, "failed": 0},
                        "tasks": [
                            {
                                "task_id": "task-1",
                                "artifacts": {
                                    "agent_patch": {
                                        "path": "task-1/agent.patch",
                                        "bytes": 19,
                                        "sha256": "not-used-by-ingest",
                                    }
                                },
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            ledger = root / "ledger.jsonl"
            row = append_patchgym_run(ledger, run_dir)
            self.assertEqual(row["metadata"]["kind"], "patchgym.run")
            self.assertEqual(row["status"], "pass")
            self.assertTrue(verify_ledger(ledger)["valid"])


if __name__ == "__main__":
    unittest.main()
