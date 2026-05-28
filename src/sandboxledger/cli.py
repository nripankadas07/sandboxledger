from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .core import append_record, create_record, verify_ledger


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="sandboxledger")
    sub = parser.add_subparsers(dest="subcommand", required=True)
    record = sub.add_parser("record", help="append a run record")
    record.add_argument("ledger")
    record.add_argument("--command", dest="run_command", required=True)
    record.add_argument("--status", required=True)
    record.add_argument("--artifact", action="append", default=[])
    verify = sub.add_parser("verify", help="verify a ledger")
    verify.add_argument("ledger")
    args = parser.parse_args(argv)
    if args.subcommand == "record":
        row = append_record(args.ledger, create_record(args.run_command, args.status, artifacts=args.artifact))
        print(json.dumps(row, indent=2, sort_keys=True))
        return 0
    if args.subcommand == "verify":
        result = verify_ledger(args.ledger)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["valid"] else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
