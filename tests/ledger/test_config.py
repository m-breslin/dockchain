import csv
import json
from pathlib import Path

import pytest

from dockchain.ledger.config import load_pipeline_config, run_configured_pipeline
from dockchain.ledger.operations import create_default_registry
from dockchain.ledger.store import JsonObjectStore

SAMPLE_CSV = Path(__file__).parents[2] / "samples" / "test_files" / "sample_orders.csv"


def test_yaml_pipeline_reads_transforms_and_writes_csv(tmp_path):
    output_path = tmp_path / "output" / "orders.csv"
    config_path = tmp_path / "sample.yaml"
    config_path.write_text(
        f"""
version: 1
name: sample-orders
steps:
  - name: extract
    use: file.read_csv
    with:
      path: {SAMPLE_CSV}
  - name: transform
    use: records.add_column
    with:
      name: line_total
      expression: quantity * unit_price
  - name: load
    use: file.write_csv
    with:
      path: {output_path}
""",
        encoding="utf-8",
    )
    store = JsonObjectStore(tmp_path / "artifacts")

    run_id, _run_hash = run_configured_pipeline(config_path, store)
    _record_hash, run_record = store.load_run(run_id)
    artifacts = [
        store.load(artifact_hash, run_id) for artifact_hash in run_record["artifact_hashes"]
    ]
    with output_path.open(encoding="utf-8", newline="") as output_file:
        output_records = list(csv.DictReader(output_file))

    assert [artifact["step_name"] for artifact in artifacts] == [
        "extract",
        "transform",
        "load",
    ]
    assert artifacts[1]["data"]["records"][0]["line_total"] == "42.00"
    assert output_records[0]["line_total"] == "42.00"
    assert output_records[1]["line_total"] == "48.00"


def test_json_pipeline_and_custom_operation_can_be_registered(tmp_path):
    source_path = tmp_path / "source.json"
    source_path.write_text(json.dumps([{"value": 2}]), encoding="utf-8")
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        f"""
version: 1
name: custom-pipeline
steps:
  - name: extract
    use: file.read_json
    with:
      path: {source_path}
  - name: custom
    use: example.double
""",
        encoding="utf-8",
    )
    registry = create_default_registry()
    registry.register(
        "example.double",
        lambda input_data, _settings, _directory: [
            {"value": row["value"] * 2} for row in input_data["records"]
        ],
    )

    run_id, _run_hash = run_configured_pipeline(
        config_path,
        JsonObjectStore(tmp_path / "artifacts"),
        registry,
    )
    _record_hash, run_record = JsonObjectStore(tmp_path / "artifacts").load_run(run_id)
    artifacts = [
        JsonObjectStore(tmp_path / "artifacts").load(artifact_hash, run_id)
        for artifact_hash in run_record["artifact_hashes"]
    ]

    assert artifacts[-1]["data"] == [{"value": 4}]


def test_config_reports_unknown_operations_as_clear_errors(tmp_path):
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        """
version: 1
name: bad-pipeline
steps:
  - name: extract
    use: file.not_real
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown operation 'file.not_real'"):
        run_configured_pipeline(config_path, JsonObjectStore(tmp_path / "artifacts"))


def test_config_rejects_unknown_fields_before_running(tmp_path):
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        """
version: 1
name: bad-pipeline
steps:
  - name: extract
    use: file.read_csv
    settings:
      path: source.csv
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown keys in step"):
        load_pipeline_config(config_path)
