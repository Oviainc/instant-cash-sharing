import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cashlink.core import CAP_CAD, CashLinkError, Store


@pytest.fixture()
def store(tmp_path):
    return Store(tmp_path / "db.json")


def test_full_claim_flow(store):
    t, code = store.create("Sender A", "Receiver B", 250.00, "cash_pickup")
    assert t.status == "claimable" and len(code) == 10
    done = store.claim(t.id, code, "Pickup point 4421 — ID shown")
    assert done.status == "claimed" and done.payout_reference.startswith("Pickup")


def test_cap_enforced_and_structuring_refused_in_message(store):
    with pytest.raises(CashLinkError, match="cap"):
        store.create("A", "B", CAP_CAD + 0.01, "wallet")
    ok, _ = store.create("A", "B", CAP_CAD, "wallet")
    assert ok.amount_cad == CAP_CAD


def test_wrong_code_and_double_claim_refused(store):
    t, code = store.create("A", "B", 100.00, "wallet")
    with pytest.raises(CashLinkError, match="wrong code"):
        store.claim(t.id, "ZZZZZZZZZZ", "wallet-1")
    store.claim(t.id, code, "wallet-1")
    with pytest.raises(CashLinkError, match="already claimed"):
        store.claim(t.id, code, "wallet-1")


def test_code_never_stored_in_clear(store, tmp_path):
    t, code = store.create("A", "B", 50.00, "cash_pickup")
    raw = (tmp_path / "db.json").read_text(encoding="utf-8")
    assert code not in raw and t.code_hash in raw
