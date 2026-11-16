"""CLI demo of the claim-link flow (local prototype, no real money).

    python -m cashlink create --sender "Sender" --recipient "Receiver" \
        --amount 250 --method cash_pickup
    # -> prints the transfer id and the one-time claim code
    python -m cashlink claim --id CL-XXXX --code ABC123XYZ9 \
        --payout-ref "Pickup point 4421, ID shown"
    python -m cashlink list
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import CashLinkError, Store

DB = Path("cashlink-demo.json")


def main() -> int:
    ap = argparse.ArgumentParser(prog="cashlink")
    ap.add_argument("--db", default=str(DB))
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("--sender", required=True)
    c.add_argument("--recipient", required=True)
    c.add_argument("--amount", type=float, required=True)
    c.add_argument("--method", default="cash_pickup",
                   choices=["cash_pickup", "wallet"])
    k = sub.add_parser("claim")
    k.add_argument("--id", required=True)
    k.add_argument("--code", required=True)
    k.add_argument("--payout-ref", required=True)
    x = sub.add_parser("cancel")
    x.add_argument("--id", required=True)
    sub.add_parser("list")
    args = ap.parse_args()

    store = Store(Path(args.db))
    try:
        if args.cmd == "create":
            t, code = store.create(args.sender, args.recipient,
                                   args.amount, args.method)
            print(json.dumps({**t.public_view(), "claim_code": code,
                              "note": "send the code to the recipient — "
                                      "shown once, stored hashed"},
                             indent=2, ensure_ascii=False))
        elif args.cmd == "claim":
            t = store.claim(args.id, args.code, args.payout_ref)
            print(json.dumps(t.public_view(), indent=2, ensure_ascii=False))
        elif args.cmd == "cancel":
            t = store.cancel(args.id)
            print(json.dumps(t.public_view(), indent=2, ensure_ascii=False))
        elif args.cmd == "list":
            for t in store.list_all():
                print(json.dumps(t.public_view(), ensure_ascii=False))
    except CashLinkError as exc:
        print(f"REFUSED: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
