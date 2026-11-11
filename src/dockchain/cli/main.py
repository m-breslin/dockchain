"""Simple commands for running and inspecting the local JSON ledger."""

import csv
import json
from pathlib import Path
from typing import Annotated, Any

import typer

from dockchain.examples.sample_pipeline import run_sample_pipeline
from dockchain.ledger.store import JsonObjectStore

app = typer.Typer(
    no_args_is_help=True, help="Run local Dockchain pipelines and inspect the ledger."
)


@app.command("run-sample")
def run_sample(
    input_file: Annotated[Path, typer.Option("--input", exists=True, dir_okay=False)],
    artifacts_dir: Annotated[Path, typer.Option("--artifacts-dir")] = Path("artifacts"),
) -> None:
    """Run the included sample pipeline and record each step."""
    store = JsonObjectStore(artifacts_dir)
    try:
        run_id, run_hash = run_sample_pipeline(input_file, store)
    except (OSError, ValueError, UnicodeError, csv.Error) as error:
        typer.echo(f"Pipeline failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f"Run completed: {run_id}")
    typer.echo(f"Run record: {run_hash}")
    typer.echo(f"Run artifacts: {artifacts_dir / 'runs' / run_id}")


@app.command()
def runs(
    artifacts_dir: Annotated[Path, typer.Option("--artifacts-dir")] = Path("artifacts"),
) -> None:
    """List recorded pipeline runs."""
    store = JsonObjectStore(artifacts_dir)
    try:
        run_records = store.list_records("run")
    except (OSError, ValueError) as error:
        typer.echo(f"Could not list runs: {error}", err=True)
        raise typer.Exit(code=1) from error

    if not run_records:
        typer.echo("No runs found.")
        return

    for run_hash, record in sorted(run_records, key=_run_sort_key):
        typer.echo(
            f"{record['status']}  {record['started_at']}  "
            f"run_id={record['run_id']}  run_record={run_hash}"
        )


@app.command()
def show(
    run_id: str,
    artifacts_dir: Annotated[Path, typer.Option("--artifacts-dir")] = Path("artifacts"),
) -> None:
    """Show a run and the hash-verified records in its step folders."""
    store = JsonObjectStore(artifacts_dir)
    try:
        run_hash, run_record = store.load_run(run_id)
        details = {
            "run_record_hash": run_hash,
            "run_id": run_id,
            "run": run_record,
            "pipeline_definition": store.load(run_record["pipeline_definition_hash"], run_id),
            "events": [store.load(event_hash) for event_hash in run_record["event_hashes"]],
            "artifacts": [
                store.load(artifact_hash, run_id) for artifact_hash in run_record["artifact_hashes"]
            ],
        }
    except (OSError, ValueError) as error:
        typer.echo(f"Could not load run: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps(details, indent=2, sort_keys=True))


@app.command()
def verify(
    artifacts_dir: Annotated[Path, typer.Option("--artifacts-dir")] = Path("artifacts"),
) -> None:
    """Verify that every stored JSON file matches its hash name."""
    store = JsonObjectStore(artifacts_dir)
    try:
        verified_count = store.verify_all()
    except (OSError, ValueError) as error:
        typer.echo(f"Verification failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f"Verified {verified_count} JSON records.")


def _run_sort_key(item: tuple[str, dict[str, Any]]) -> tuple[str, str]:
    run_hash, record = item
    return str(record["started_at"]), run_hash


if __name__ == "__main__":
    app()
