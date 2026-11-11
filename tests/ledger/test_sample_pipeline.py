import base64
from pathlib import Path

from dockchain.examples.sample_pipeline import run_sample_pipeline
from dockchain.ledger.store import JsonObjectStore

SAMPLE_CSV = Path(__file__).parents[2] / "samples" / "test_files" / "sample_orders.csv"


def test_sample_pipeline_saves_source_transform_and_load_steps(tmp_path):
    store = JsonObjectStore(tmp_path / "artifacts")

    run_id, _run_hash = run_sample_pipeline(SAMPLE_CSV, store)
    _record_hash, run_record = store.load_run(run_id)
    artifacts = [
        store.load(artifact_hash, run_id) for artifact_hash in run_record["artifact_hashes"]
    ]
    events = [store.load(event_hash, run_id) for event_hash in run_record["event_hashes"]]

    assert [artifact["step_name"] for artifact in artifacts] == [
        "extract",
        "transform",
        "load",
    ]
    assert base64.b64decode(artifacts[0]["data"]["content_base64"]) == SAMPLE_CSV.read_bytes()
    assert artifacts[1]["data"][0]["line_total"] == "42.00"
    assert artifacts[1]["data"][3]["line_total"] == "49.98"
    assert artifacts[2]["data"]["record_count"] == 5
    assert [event["step_name"] for event in events if "step_name" in event] == [
        "extract",
        "transform",
        "load",
    ]
