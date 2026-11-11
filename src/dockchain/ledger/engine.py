"""Run ordered, reusable steps and record each result as JSON."""

import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from dockchain.ledger.store import JsonObjectStore


@dataclass
class PipelineStep:
    """A named operation and the function that runs it."""

    name: str
    operation: str
    run: Callable[[Any], Any]
    metadata: dict[str, Any]


def run_pipeline(
    pipeline_name: str,
    steps: list[PipelineStep],
    store: JsonObjectStore,
) -> tuple[str, str]:
    """Run each step in order and return the run ID and final record hash."""
    if not pipeline_name.strip():
        raise ValueError("Pipeline name cannot be empty")
    if not steps:
        raise ValueError("Pipeline must have at least one step")
    _validate_steps(steps)

    started_at = _timestamp()
    run_id = _run_id(pipeline_name, started_at)
    step_width = max(2, len(str(len(steps))))
    event_hashes: list[str] = []
    artifact_hashes: list[str] = []

    definition = {
        "record_type": "pipeline_definition",
        "schema_version": 1,
        "pipeline_name": pipeline_name,
        "steps": [
            {
                "name": step.name,
                "operation": step.operation,
                "metadata": step.metadata,
            }
            for step in steps
        ],
    }
    definition_hash = store.save(definition, run_id, "pipeline")
    start_event = {
        "record_type": "event",
        "schema_version": 1,
        "event_type": "run_started",
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "pipeline_definition_hash": definition_hash,
        "sequence": 0,
        "created_at": started_at,
    }
    event_hashes.append(store.save(start_event, run_id, "run"))

    current_value: Any = None
    previous_artifact_hash: str | None = None
    active_step_directory = "run"
    active_step_name = "run"

    try:
        for step_number, step in enumerate(steps, start=1):
            step_directory = f"steps/{step_number:0{step_width}d}-{step.name}"
            active_step_name = step.name
            active_step_directory = f"{step_directory}/events"
            current_value = step.run(current_value)
            artifact = {
                "record_type": "step_artifact",
                "schema_version": 1,
                "run_id": run_id,
                "step_name": step.name,
                "step_number": step_number,
                "input_artifact_hash": previous_artifact_hash,
                "created_at": _timestamp(),
                "data": current_value,
            }
            artifact_hash = store.save(artifact, run_id, f"{step_directory}/artifacts")
            artifact_hashes.append(artifact_hash)

            event = {
                "record_type": "event",
                "schema_version": 1,
                "event_type": "step_completed",
                "run_id": run_id,
                "step_name": step.name,
                "step_number": step_number,
                "artifact_hash": artifact_hash,
                "sequence": len(event_hashes),
                "created_at": _timestamp(),
                "previous_event_hash": event_hashes[-1],
            }
            event_hashes.append(store.save(event, run_id, active_step_directory))
            previous_artifact_hash = artifact_hash

        status = "completed"
    except Exception as error:
        failed_event = {
            "record_type": "event",
            "schema_version": 1,
            "event_type": "step_failed",
            "run_id": run_id,
            "step_name": active_step_name,
            "sequence": len(event_hashes),
            "created_at": _timestamp(),
            "previous_event_hash": event_hashes[-1],
            "error_type": type(error).__name__,
            "message": str(error),
        }
        event_hashes.append(store.save(failed_event, run_id, active_step_directory))
        status = "failed"
        _save_run_record(
            store,
            run_id,
            pipeline_name,
            definition_hash,
            started_at,
            event_hashes,
            artifact_hashes,
            status,
        )
        raise

    run_record_hash = _save_run_record(
        store,
        run_id,
        pipeline_name,
        definition_hash,
        started_at,
        event_hashes,
        artifact_hashes,
        status,
    )
    return run_id, run_record_hash


def _save_run_record(
    store: JsonObjectStore,
    run_id: str,
    pipeline_name: str,
    definition_hash: str,
    started_at: str,
    event_hashes: list[str],
    artifact_hashes: list[str],
    status: str,
) -> str:
    record = {
        "record_type": "run",
        "schema_version": 1,
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "pipeline_definition_hash": definition_hash,
        "started_at": started_at,
        "completed_at": _timestamp(),
        "status": status,
        "event_hashes": event_hashes,
        "artifact_hashes": artifact_hashes,
    }
    return store.save(record, run_id, "run")


def _validate_steps(steps: list[PipelineStep]) -> None:
    seen_names = set()
    for step in steps:
        if re.fullmatch(r"[a-z0-9][a-z0-9_-]*", step.name) is None:
            raise ValueError(f"Invalid step name: {step.name}")
        if step.name in seen_names:
            raise ValueError(f"Step names must be unique: {step.name}")
        if not step.operation.strip():
            raise ValueError(f"Step operation cannot be empty: {step.name}")
        seen_names.add(step.name)


def _run_id(pipeline_name: str, started_at: str) -> str:
    identity = json.dumps(
        {"pipeline_name": pipeline_name, "started_at": started_at},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(identity).hexdigest()


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()
