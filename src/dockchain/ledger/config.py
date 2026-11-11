"""Load a simple YAML pipeline definition and connect its operations."""

import json
from pathlib import Path
from typing import Any

import yaml

from dockchain.ledger.engine import PipelineStep, run_pipeline
from dockchain.ledger.operations import OperationRegistry, create_default_registry
from dockchain.ledger.store import JsonObjectStore


def load_pipeline_config(config_path: Path) -> dict[str, Any]:
    """Read and validate the basic shape of a pipeline YAML file."""
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML in {config_path}: {error}") from error

    if not isinstance(config, dict):
        raise ValueError("Pipeline config must be a YAML object")
    unexpected_config_keys = set(config) - {"version", "name", "steps"}
    if unexpected_config_keys:
        raise ValueError(
            f"Unknown pipeline config keys: {', '.join(sorted(unexpected_config_keys))}"
        )
    if config.get("version") != 1:
        raise ValueError("Pipeline config must set version: 1")
    if not isinstance(config.get("name"), str) or not config["name"].strip():
        raise ValueError("Pipeline config must include a non-empty name")
    steps = config.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("Pipeline config must include at least one step")

    for position, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValueError(f"Step {position} must be a YAML object")
        unexpected_step_keys = set(step) - {"name", "use", "with"}
        if unexpected_step_keys:
            raise ValueError(
                f"Unknown keys in step {position}: {', '.join(sorted(unexpected_step_keys))}"
            )
        if not isinstance(step.get("name"), str) or not step["name"]:
            raise ValueError(f"Step {position} must include a name")
        if not isinstance(step.get("use"), str) or not step["use"]:
            raise ValueError(f"Step '{step['name']}' must include an operation in 'use'")
        settings = step.get("with", {})
        if not isinstance(settings, dict):
            raise ValueError(f"Step '{step['name']}' settings in 'with' must be an object")

    try:
        json.dumps(config, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("Pipeline config values must be valid JSON values") from error

    return config


def run_configured_pipeline(
    config_path: Path,
    store: JsonObjectStore,
    registry: OperationRegistry | None = None,
) -> tuple[str, str]:
    """Load a YAML definition and run it using registered operations."""
    config = load_pipeline_config(config_path)
    operation_registry = registry or create_default_registry()
    config_directory = config_path.resolve().parent
    steps = []

    for step_config in config["steps"]:
        operation_name = step_config["use"]
        settings = step_config.get("with", {})

        def run_step(
            input_data: Any,
            operation_name: str = operation_name,
            settings: dict[str, Any] = settings,
        ) -> Any:
            return operation_registry.run(
                operation_name,
                input_data,
                settings,
                config_directory,
            )

        steps.append(
            PipelineStep(
                name=step_config["name"],
                operation=operation_name,
                run=run_step,
                metadata=settings,
            )
        )

    return run_pipeline(config["name"], steps, store)
