# Dockchain

**Immutable, replayable ETL pipelines built with containerized execution and complete execution lineage.**

Dockchain is a lightweight, configuration-driven ETL platform designed to make data pipelines easier to build, execute, inspect, and reproduce.

Build pipelines through guided configuration or YAML, execute transformations in isolated containers, and maintain a verifiable history of the data and operations behind every execution.

**Build. Execute. Track. Replay.**

---

## What is Dockchain?

Traditional ETL pipelines can be difficult to debug and reproduce. Data changes, APIs return different responses, dependencies evolve, and transformation logic gets updated. Without preserving the context of an execution, reconstructing what happened can become difficult or impossible.

Dockchain aims to solve this by treating every pipeline execution as a traceable, preservable event.

Rather than only recording where data came from or what transformations were performed, Dockchain is designed to preserve the actual inputs, outputs, configuration, and execution context needed to understand and reproduce pipeline behavior.

## Core Principles

- **Configuration-driven:** Define pipelines through readable YAML and guided configuration rather than requiring custom code for every operation.
- **Containerized execution:** Run pipelines in isolated, reproducible runtime environments.
- **Execution lineage:** Track the operations, dependencies, inputs, outputs, and relationships behind each execution.
- **Data preservation:** Retain historical inputs and outputs so past executions can be inspected and reconstructed.
- **Replayability:** Revisit historical executions using their original captured inputs instead of silently retrieving changing external data.
- **Extensibility:** Support custom Python and SQL alongside standardized pipeline operations.

## Technology

Dockchain is being built around the following technologies:

| Component | Technology |
|---|---|
| Language | Python |
| Configuration | YAML |
| Data validation | Pydantic |
| Processing engine | Polars |
| Execution environment | Docker |
| CLI | Typer |
| Terminal interface | Textual |
| Package management | uv |

## Project Status

<badge color="warning">Early development</badge>

Dockchain is currently under active development. Its initial focus is establishing the core execution architecture, configuration system, containerized runtime, and execution history model.

Planned capabilities include:

- Guided pipeline creation
- YAML-based pipeline definitions
- API and database connectors
- Polars-powered transformations
- CSV and database destinations
- Containerized pipeline execution
- Execution history and artifact preservation
- Historical execution replay
- Pipeline comparison and debugging

Features are subject to change as the architecture develops.

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/)

### Clone the repository

```bash
git clone https://github.com/m-breslin/dockchain.git
cd dockchain
```

### Install dependencies

```bash
make install-deps
```

### Explore the CLI

```bash
uv run dockchain --help
```

### Run the sample pipeline

The engine is generic: a pipeline is an ordered list of named steps, each with
an operation and a function. The sample pipeline uses it to extract the source
CSV, calculate order totals, and load the records into the run artifacts.

```bash
uv run dockchain run-sample --input samples/test_files/sample_orders.csv
uv run dockchain runs
uv run dockchain show <run-id>
uv run dockchain verify
```

Each run has a readable directory containing its own ordered steps. The
records inside are JSON files named by the SHA-256 hash of their exact
contents; records link to each other by hash. No database file is used.

```text
artifacts/
└── runs/
    └── <run-id>/
        ├── pipeline/
        ├── run/
        └── steps/
            ├── 01-extract/
            │   ├── artifacts/
            │   └── events/
            ├── 02-transform/
            │   ├── artifacts/
            │   └── events/
            └── 03-load/
                ├── artifacts/
                └── events/
```

The `artifacts/` directory is local output and is excluded from Git. The sample
CSV is retained in `samples/test_files/` for manual runs and automated tests.

## Development

Dockchain uses `uv` for Python dependency management and a Makefile for common development tasks.

| Command | Description |
|---|---|
| `make install-deps` | Install development dependencies and hooks |
| `make sync-deps` | Synchronize dependencies |
| `make update-deps` | Upgrade dependencies |
| `make test` | Run tests |
| `make lint` | Run Ruff linting |
| `make format` | Format source code |
| `make type-check` | Run MyPy |
| `make check` | Run all quality checks |
| `make build` | Build the Python package |
| `make docker-build` | Build the runtime Docker image |

## Project Structure

```text
dockchain/
├── src/
│   └── dockchain/
│       ├── cli/
│       ├── interface/
│       ├── core/
│       ├── execution/
│       ├── runtime/
│       ├── connectors/
│       ├── transformations/
│       ├── ledger/
│       ├── storage/
│       ├── plugins/
│       └── schemas/
├── runtime/
├── examples/
├── tests/
├── docs/
├── .devcontainer/
├── pyproject.toml
├── uv.lock
├── Makefile
└── .pre-commit-config.yaml
```

## Design Philosophy

Dockchain is intended to be simple on the surface and powerful underneath.

A user should be able to configure a basic pipeline without writing Python, while an experienced developer should be able to extend the same pipeline with custom logic when needed.

The configuration, execution engine, and preservation layer should work together as one cohesive system rather than requiring users to assemble and maintain multiple disconnected tools.

## Contributing

Dockchain is in early development, and contributions, feedback, and architectural discussions are welcome.

Before submitting changes:

```bash
make check
```

Please open an issue to discuss substantial changes or proposed features before submitting a pull request.

## License

License information will be added before the first public release.
