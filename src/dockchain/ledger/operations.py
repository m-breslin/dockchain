"""Reusable operations that pipeline configuration can select by name."""

import ast
import base64
import csv
import hashlib
import io
import json
import operator
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

Operation = Callable[[Any, dict[str, Any], Path], Any]


class OperationRegistry:
    """Map simple operation names to the functions that run them."""

    def __init__(self) -> None:
        self._operations: dict[str, Operation] = {}

    def register(self, name: str, operation: Operation) -> None:
        """Add an operation that can be used in a pipeline config."""
        if not name or name in self._operations:
            raise ValueError(f"Operation name is empty or already registered: {name}")
        self._operations[name] = operation

    def run(
        self,
        name: str,
        input_data: Any,
        settings: dict[str, Any],
        config_directory: Path,
    ) -> Any:
        """Run the named operation or report that it is not available."""
        operation = self._operations.get(name)
        if operation is None:
            available = ", ".join(sorted(self._operations))
            raise ValueError(f"Unknown operation '{name}'. Available operations: {available}")
        return operation(input_data, settings, config_directory)


def create_default_registry() -> OperationRegistry:
    """Create the built-in file and record operations."""
    registry = OperationRegistry()
    registry.register("file.read_csv", _read_csv)
    registry.register("file.read_json", _read_json)
    registry.register("records.add_column", _add_column)
    registry.register("file.write_csv", _write_csv)
    registry.register("file.write_json", _write_json)
    return registry


def _read_csv(_input_data: Any, settings: dict[str, Any], config_directory: Path) -> dict[str, Any]:
    path = _configured_path(settings, "path", config_directory)
    content = path.read_bytes()
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
    return {
        "format": "csv",
        "records": rows,
        "source": _source_details(path, content),
    }


def _read_json(
    _input_data: Any, settings: dict[str, Any], config_directory: Path
) -> dict[str, Any]:
    path = _configured_path(settings, "path", config_directory)
    content = path.read_bytes()
    value = json.loads(content)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError(f"JSON source must contain a list of objects: {path}")
    return {
        "format": "json",
        "records": value,
        "source": _source_details(path, content),
    }


def _add_column(
    input_data: Any,
    settings: dict[str, Any],
    _config_directory: Path,
) -> dict[str, Any]:
    records = _records_from(input_data)
    column_name = settings.get("name")
    expression = settings.get("expression")
    if not isinstance(column_name, str) or not column_name:
        raise ValueError("records.add_column requires a non-empty 'name'")
    if not isinstance(expression, str) or not expression:
        raise ValueError("records.add_column requires an 'expression'")

    transformed_records = []
    for row_number, record in enumerate(records, start=1):
        transformed = dict(record)
        transformed[column_name] = _evaluate_expression(expression, record, row_number)
        transformed_records.append(transformed)

    return {**input_data, "records": transformed_records}


def _write_csv(
    input_data: Any,
    settings: dict[str, Any],
    config_directory: Path,
) -> dict[str, Any]:
    records = _records_from(input_data)
    path = _configured_path(settings, "path", config_directory)
    if records:
        field_names = list(records[0])
    else:
        field_names = settings.get("fields", [])
    if not field_names:
        raise ValueError("file.write_csv requires records or a non-empty 'fields' list")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=field_names, extrasaction="raise")
        writer.writeheader()
        writer.writerows(records)
    return _written_file_details(path, len(records), "csv")


def _write_json(
    input_data: Any,
    settings: dict[str, Any],
    config_directory: Path,
) -> dict[str, Any]:
    records = _records_from(input_data)
    path = _configured_path(settings, "path", config_directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"{json.dumps(records, indent=2, ensure_ascii=False)}\n".encode()
    path.write_bytes(content)
    return {
        "format": "json",
        "path": str(path),
        "record_count": len(records),
        "size_bytes": len(content),
        "content_sha256": hashlib.sha256(content).hexdigest(),
    }


def _configured_path(
    settings: dict[str, Any],
    key: str,
    config_directory: Path,
) -> Path:
    value = settings.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Operation requires a non-empty '{key}' path")
    path = Path(value)
    if not path.is_absolute():
        path = config_directory / path
    return path.resolve()


def _source_details(path: Path, content: bytes) -> dict[str, Any]:
    return {
        "file_name": path.name,
        "path": str(path),
        "size_bytes": len(content),
        "content_sha256": hashlib.sha256(content).hexdigest(),
        "content_base64": base64.b64encode(content).decode("ascii"),
    }


def _written_file_details(path: Path, record_count: int, file_format: str) -> dict[str, Any]:
    content = path.read_bytes()
    return {
        "format": file_format,
        "path": str(path),
        "record_count": record_count,
        "size_bytes": len(content),
        "content_sha256": hashlib.sha256(content).hexdigest(),
    }


def _records_from(input_data: Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list) and all(isinstance(row, dict) for row in input_data):
        return input_data
    if isinstance(input_data, dict):
        records = input_data.get("records")
        if isinstance(records, list) and all(isinstance(row, dict) for row in records):
            return records
    raise ValueError("Operation expects a list of record objects from the previous step")


def _evaluate_expression(
    expression: str,
    record: dict[str, Any],
    row_number: int,
) -> str:
    try:
        parsed_expression = ast.parse(expression, mode="eval")
        result = _evaluate_node(parsed_expression.body, record)
    except (ArithmeticError, KeyError, SyntaxError, TypeError, ValueError) as error:
        raise ValueError(
            f"Could not evaluate expression for record {row_number}: {error}"
        ) from error
    return format(result, "f")


def _evaluate_node(node: ast.expr, record: dict[str, Any]) -> Decimal:
    operations: dict[type[ast.operator], Callable[[Decimal, Decimal], Decimal]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
    if isinstance(node, ast.Name):
        value = record.get(node.id)
        if value is None:
            raise ValueError(f"Record does not have a value for '{node.id}'")
        return Decimal(str(value))
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Decimal(str(node.value))
    if isinstance(node, ast.BinOp) and type(node.op) in operations:
        return operations[type(node.op)](
            _evaluate_node(node.left, record),
            _evaluate_node(node.right, record),
        )
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_node(node.operand, record)
        return value if isinstance(node.op, ast.UAdd) else -value
    raise ValueError("Expression supports numeric values and +, -, *, / only")
