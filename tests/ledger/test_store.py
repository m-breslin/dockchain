import hashlib
import json

import pytest

from dockchain.ledger.store import JsonObjectStore


def test_store_uses_hash_filenames_and_named_run_folders(tmp_path):
    store = JsonObjectStore(tmp_path / "artifacts")
    run_id = "a" * 64
    record = {"record_type": "step_artifact", "step_name": "extract"}

    record_hash = store.save(record, run_id, "steps/01-extract/artifacts")
    record_path = (
        store.runs_dir / run_id / "steps" / "01-extract" / "artifacts" / f"{record_hash}.json"
    )

    assert hashlib.sha256(record_path.read_bytes()).hexdigest() == record_hash
    assert json.loads(record_path.read_bytes()) == record
    assert store.load(record_hash, run_id) == record
    assert store.verify_all() == 1


def test_load_rejects_changed_file_contents(tmp_path):
    store = JsonObjectStore(tmp_path / "artifacts")
    run_id = "b" * 64
    record_hash = store.save({"record_type": "event"}, run_id, "run")
    record_path = store.runs_dir / run_id / "run" / f"{record_hash}.json"
    record_path.write_text('{"record_type": "changed"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Object hash mismatch"):
        store.load(record_hash, run_id)
