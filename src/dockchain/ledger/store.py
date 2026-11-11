"""Save and verify hash-named JSON records grouped by pipeline run and step."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any


class JsonObjectStore:
    """Store records under artifacts/runs/<run-id>/<run-section>/<record-hash>.json."""

    def __init__(self, artifacts_dir: Path) -> None:
        self.runs_dir = artifacts_dir / "runs"

    def save(self, record: dict[str, Any], run_id: str, record_directory: str) -> str:
        """Write a record to its run directory, named by its content hash."""
        self._validate_run_id(run_id)
        self._validate_record_directory(record_directory)
        content = _json_bytes(record)
        object_hash = hashlib.sha256(content).hexdigest()
        object_path = self._path_for(run_id, record_directory, object_hash)
        object_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with object_path.open("xb") as object_file:
                object_file.write(content)
        except FileExistsError as error:
            if object_path.read_bytes() != content:
                raise ValueError(
                    f"Existing object does not match its hash: {object_hash}"
                ) from error

        return object_hash

    def load(self, object_hash: str, run_id: str | None = None) -> dict[str, Any]:
        """Load a record only when its file contents match the requested hash."""
        if re.fullmatch(r"[0-9a-f]{64}", object_hash) is None:
            raise ValueError("Object hash must be 64 lowercase hexadecimal characters")

        if run_id is None:
            object_paths = [
                path for path in self.runs_dir.rglob(f"{object_hash}.json") if path.is_file()
            ]
        else:
            self._validate_run_id(run_id)
            object_paths = [
                path
                for path in (self.runs_dir / run_id).rglob(f"{object_hash}.json")
                if path.is_file()
            ]

        if not object_paths:
            raise FileNotFoundError(f"Object not found: {object_hash}")

        return self._load_path(object_paths[0], object_hash)

    def list_hashes(self) -> list[str]:
        """Return hashes for every JSON record stored under a run directory."""
        if not self.runs_dir.exists():
            return []
        return sorted({path.stem for path in self.runs_dir.rglob("*.json") if path.is_file()})

    def list_records(self, record_type: str) -> list[tuple[str, dict[str, Any]]]:
        """Load all verified records of a given type."""
        records: list[tuple[str, dict[str, Any]]] = []
        if not self.runs_dir.exists():
            return records
        for path in self.runs_dir.rglob("*.json"):
            if not path.is_file():
                continue
            record = self._load_path(path, path.stem)
            if record.get("record_type") == record_type:
                records.append((path.stem, record))
        return records

    def load_run(self, run_id: str) -> tuple[str, dict[str, Any]]:
        """Load the final run record for a run ID."""
        self._validate_run_id(run_id)
        run_directory = self.runs_dir / run_id / "run"
        for path in sorted(run_directory.glob("*.json")):
            run_hash = path.stem
            record = self.load(run_hash, run_id)
            if record.get("record_type") == "run":
                return run_hash, record
        raise FileNotFoundError(f"Run record not found: {run_id}")

    def verify_all(self) -> int:
        """Verify every JSON file individually and return the number checked."""
        if not self.runs_dir.exists():
            return 0

        paths = [path for path in self.runs_dir.rglob("*.json") if path.is_file()]
        for path in paths:
            self._load_path(path, path.stem)
        return len(paths)

    def _path_for(self, run_id: str, record_directory: str, object_hash: str) -> Path:
        return self.runs_dir / run_id / record_directory / f"{object_hash}.json"

    @staticmethod
    def _load_path(object_path: Path, object_hash: str) -> dict[str, Any]:
        if re.fullmatch(r"[0-9a-f]{64}", object_hash) is None:
            raise ValueError("Object hash must be 64 lowercase hexadecimal characters")
        content = object_path.read_bytes()
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != object_hash:
            raise ValueError(
                f"Object hash mismatch for {object_hash}: file contents hash to {actual_hash}"
            )
        record = json.loads(content)
        if not isinstance(record, dict):
            raise ValueError(f"Object must contain a JSON object: {object_hash}")
        return record

    @staticmethod
    def _validate_run_id(run_id: str) -> None:
        if re.fullmatch(r"[0-9a-f]{64}", run_id) is None:
            raise ValueError("Run ID must be 64 lowercase hexadecimal characters")

    @staticmethod
    def _validate_record_directory(record_directory: str) -> None:
        parts = record_directory.split("/")
        if not parts or any(re.fullmatch(r"[a-z0-9][a-z0-9_-]*", part) is None for part in parts):
            raise ValueError("Record directory must use simple names separated by slashes")


def _json_bytes(record: dict[str, Any]) -> bytes:
    json_text = json.dumps(
        record,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )
    return f"{json_text}\n".encode()
