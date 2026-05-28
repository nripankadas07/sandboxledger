from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
import io
import json
import unittest

from sandboxledger import append_record, create_record, verify_ledger
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


if __name__ == "__main__":
    unittest.main()
