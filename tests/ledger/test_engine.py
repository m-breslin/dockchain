import pytest

from dockchain.ledger.engine import PipelineStep, run_pipeline
from dockchain.ledger.store import JsonObjectStore


def test_pipeline_engine_records_named_steps_under_one_run(tmp_path):
    store = JsonObjectStore(tmp_path / "artifacts")

    def extract(_previous):
        return {"value": 2}

    def transform(data):
        return data["value"] * 2

    def load(data):
        return {"saved": data}

    steps = [
        PipelineStep("extract", "get_value", extract, {}),
        PipelineStep("transform", "double_value", transform, {}),
        PipelineStep("load", "save_result", load, {}),
    ]

    run_id, run_hash = run_pipeline("test-pipeline", steps, store)
    record_hash, run_record = store.load_run(run_id)
    output_records = [
        store.load(artifact_hash, run_id) for artifact_hash in run_record["artifact_hashes"]
    ]
    run_directory = store.runs_dir / run_id
    step_directories = sorted(path.name for path in (run_directory / "steps").iterdir())

    assert record_hash == run_hash
    assert run_record["status"] == "completed"
    assert step_directories == [
        "01-extract",
        "02-transform",
        "03-load",
    ]
    assert sorted(path.name for path in run_directory.iterdir()) == [
        "pipeline",
        "run",
        "steps",
    ]
    assert [record["step_name"] for record in output_records] == [
        "extract",
        "transform",
        "load",
    ]
    assert output_records[0]["data"] == {"value": 2}
    assert output_records[1]["data"] == 4
    assert output_records[2]["data"] == {"saved": 4}
    for step_directory in (run_directory / "steps").iterdir():
        assert sorted(path.name for path in step_directory.iterdir()) == ["artifacts", "events"]
    assert all(len(path.stem) == 64 for path in run_directory.rglob("*.json"))


def test_failed_step_is_recorded_before_error_is_raised(tmp_path):
    store = JsonObjectStore(tmp_path / "artifacts")

    def fail(_previous):
        raise ValueError("step failed")

    with pytest.raises(ValueError, match="step failed"):
        run_pipeline(
            "failing-pipeline",
            [PipelineStep("extract", "read_source", fail, {})],
            store,
        )

    _run_hash, run_record = store.list_records("run")[0]
    events = [store.load(event_hash) for event_hash in run_record["event_hashes"]]

    assert run_record["status"] == "failed"
    assert events[-1]["event_type"] == "step_failed"
    assert events[-1]["step_name"] == "extract"


def test_pipeline_rejects_duplicate_step_names(tmp_path):
    store = JsonObjectStore(tmp_path / "artifacts")

    def first_source(_data):
        return 1

    def second_source(_data):
        return 2

    steps = [
        PipelineStep("extract", "read_first_source", first_source, {}),
        PipelineStep("extract", "read_second_source", second_source, {}),
    ]

    with pytest.raises(ValueError, match="must be unique"):
        run_pipeline("duplicate-steps", steps, store)
