"""Sample CSV pipeline composed from generic pipeline steps."""

import base64
import csv
import hashlib
import io
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from dockchain.ledger.engine import PipelineStep, run_pipeline
from dockchain.ledger.store import JsonObjectStore


def run_sample_pipeline(input_path: Path, store: JsonObjectStore) -> tuple[str, str]:
    """Run the sample orders file through extract, transform, and load steps."""

    def extract_source(_previous: Any) -> dict[str, Any]:
        return _extract_csv(input_path)

    steps = [
        PipelineStep(
            name="extract",
            operation="read_csv_file",
            run=extract_source,
            metadata={"input_file": input_path.name},
        ),
        PipelineStep(
            name="transform",
            operation="add_order_line_total",
            run=_transform_orders,
            metadata={"formula": "quantity * unit_price", "output_column": "line_total"},
        ),
        PipelineStep(
            name="load",
            operation="save_json_records",
            run=_load_records,
            metadata={"destination": "run_artifacts"},
        ),
    ]
    return run_pipeline("sample-orders", steps, store)


def _extract_csv(input_path: Path) -> dict[str, Any]:
    source_bytes = input_path.read_bytes()
    return {
        "file_name": input_path.name,
        "media_type": "text/csv",
        "size_bytes": len(source_bytes),
        "content_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "content_base64": base64.b64encode(source_bytes).decode("ascii"),
    }


def _transform_orders(source: dict[str, Any]) -> list[dict[str, str]]:
    source_bytes = base64.b64decode(source["content_base64"], validate=True)
    reader = csv.DictReader(io.StringIO(source_bytes.decode("utf-8")))
    if reader.fieldnames is None:
        raise ValueError("CSV file must include a header row")
    if "quantity" not in reader.fieldnames or "unit_price" not in reader.fieldnames:
        raise ValueError("CSV file must include quantity and unit_price columns")

    transformed_records = []
    for row_number, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"CSV row {row_number} has a different number of columns")
        try:
            quantity = int(row["quantity"])
            unit_price = Decimal(row["unit_price"])
        except (ValueError, InvalidOperation) as error:
            raise ValueError(
                f"CSV row {row_number} has an invalid quantity or unit_price"
            ) from error
        if not unit_price.is_finite():
            raise ValueError(f"CSV row {row_number} has a non-finite unit_price")

        transformed_row = dict(row)
        transformed_row["line_total"] = format(quantity * unit_price, "f")
        transformed_records.append(transformed_row)

    return transformed_records


def _load_records(records: list[dict[str, str]]) -> dict[str, Any]:
    """Return records as the sample pipeline's local JSON load output."""
    return {"destination": "run_artifacts", "record_count": len(records), "records": records}
