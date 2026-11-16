"""Instant cash sharing — the claim-link core.

Design target, stated honestly: a recipient needs **no account, no
login, no app**. They receive a link plus a short code, choose cash
pickup or a wallet, and show ID once at the point of payout. That is
the legal minimum everywhere this operates: anti-money-laundering law
(FINTRAC in Canada, FinCEN in the US, equivalents elsewhere) requires
the *operator* to identify senders, and cash pickup points to check
the receiver's ID against the transfer. A design promising "no ID,
ever, anywhere" cannot be run by any regulated provider — so this core
builds the lightest lawful shape instead:

- sender side: GUEST SEND — no account, no password, no login; the
  sender's identity is verified once per send by the operator (an ID
  verification reference, never raw ID data in this core). No-login is
  a UX choice; no-ID would be illegal in every corridor.
- recipient side: link + code only; ID checked once, at payout
- sender identity is verified at EVERY amount in this design — the
  per-transfer cap is a fraud/risk product limit, not a threshold
  device, and splitting to dodge a cap or a check is structuring
- one claim only; codes stored hashed; transfers expire

This is a local prototype: no real money moves, no provider is
connected. The provider route (partner network vs own MSB licence)
stays an open decision recorded in the README.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

CAP_CAD = 999.99           # per-transfer cap, under the $1,000 line
EXPIRY_HOURS = 72
CODE_ALPHABET = string.ascii_uppercase + string.digits
STATUSES = ("created", "claimable", "claimed", "expired", "cancelled")
PAYOUT_METHODS = ("cash_pickup", "wallet")


class CashLinkError(Exception):
    pass


def _hash(code: str) -> str:
    return hashlib.sha256(code.strip().upper().encode()).hexdigest()


def new_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(10))


@dataclass
class Transfer:
    id: str
    sender_label: str
    recipient_label: str
    amount_cad: float
    payout_method: str
    status: str = "created"
    code_hash: str = ""
    created_at: str = ""
    expires_at: str = ""
    claimed_at: str = ""
    payout_reference: str = ""   # set at payout: pickup location or wallet id

    def public_view(self) -> dict:
        """What a claim page may show — never the code hash."""
        return {"id": self.id, "recipient": self.recipient_label,
                "amount_cad": self.amount_cad,
                "payout_method": self.payout_method,
                "status": self.status, "expires_at": self.expires_at}


class Store:
    """JSON-file store — a prototype stand-in for a real database."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[Transfer]:
        return [Transfer(**row) for row in
                json.loads(self.path.read_text(encoding="utf-8"))]

    def _save(self, rows: list[Transfer]) -> None:
        self.path.write_text(json.dumps(
            [t.__dict__ for t in rows], indent=2, ensure_ascii=False),
            encoding="utf-8")

    def create(self, sender_label: str, recipient_label: str,
               amount_cad: float, payout_method: str,
               sender_id_ref: str = "") -> tuple[Transfer, str]:
        if not sender_id_ref.strip():
            raise CashLinkError(
                "sender identity verification is required on every send "
                "— guest send means no account and no login, not no ID; "
                "the operator verifies the sender and passes a reference")
        if amount_cad <= 0:
            raise CashLinkError("amount must be positive")
        if amount_cad > CAP_CAD:
            raise CashLinkError(
                f"per-transfer cap is CAD {CAP_CAD:.2f} (product risk "
                "limit — larger sends use the standard verified route); "
                "splitting a send to dodge the cap or a check is "
                "structuring and is refused by design")
        if payout_method not in PAYOUT_METHODS:
            raise CashLinkError(f"payout method must be one of {PAYOUT_METHODS}")
        now = datetime.now(timezone.utc)
        code = new_code()
        transfer = Transfer(
            id="CL-" + secrets.token_hex(4).upper(),
            sender_label=sender_label, recipient_label=recipient_label,
            amount_cad=round(float(amount_cad), 2),
            payout_method=payout_method, status="claimable",
            code_hash=_hash(code), created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=EXPIRY_HOURS)).isoformat())
        rows = self._load()
        rows.append(transfer)
        self._save(rows)
        return transfer, code

    def get(self, transfer_id: str) -> Transfer:
        for t in self._load():
            if t.id == transfer_id:
                return t
        raise CashLinkError(f"unknown transfer: {transfer_id}")

    def _replace(self, updated: Transfer) -> None:
        rows = [updated if t.id == updated.id else t for t in self._load()]
        self._save(rows)

    def claim(self, transfer_id: str, code: str,
              payout_reference: str) -> Transfer:
        """Recipient claim: correct code + a payout reference (pickup
        location where ID was shown, or the wallet identifier)."""
        t = self.get(transfer_id)
        if t.status == "claimed":
            raise CashLinkError("already claimed — a transfer pays out once")
        if t.status != "claimable":
            raise CashLinkError(f"transfer is {t.status}, not claimable")
        if datetime.now(timezone.utc) > datetime.fromisoformat(t.expires_at):
            t.status = "expired"
            self._replace(t)
            raise CashLinkError("transfer expired")
        if not secrets.compare_digest(_hash(code), t.code_hash):
            raise CashLinkError("wrong code")
        if not payout_reference.strip():
            raise CashLinkError(
                "a payout reference is required: the pickup point where "
                "ID is shown, or the receiving wallet")
        t.status = "claimed"
        t.claimed_at = datetime.now(timezone.utc).isoformat()
        t.payout_reference = payout_reference.strip()
        self._replace(t)
        return t

    def cancel(self, transfer_id: str) -> Transfer:
        t = self.get(transfer_id)
        if t.status == "claimed":
            raise CashLinkError("cannot cancel a claimed transfer")
        t.status = "cancelled"
        self._replace(t)
        return t

    def list_all(self) -> list[Transfer]:
        return self._load()
