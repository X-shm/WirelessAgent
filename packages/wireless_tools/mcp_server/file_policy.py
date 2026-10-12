"""Keep agent-supplied file paths inside the configured MCP data directory."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any


EMBEDDED_FILE_KEYS = {"session_file", "output_path", "waveform_file"}
MAX_JSON_FILE_BYTES = 8_000_000


class FilePolicyError(ValueError):
    pass


class FilePolicy:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or Path(tempfile.gettempdir()) / "wireless-toolbox-mcp-data").expanduser().resolve()

    def resolve(self, value: str, field: str) -> str:
        if not value.strip() or "\x00" in value:
            raise FilePolicyError(f"{field} must be a nonempty path")
        try:
            proposed = Path(value).expanduser()
            path = (proposed if proposed.is_absolute() else self.root / proposed).resolve()
        except (OSError, ValueError) as exc:
            raise FilePolicyError(f"invalid {field} path") from exc
        if path == self.root or not path.is_relative_to(self.root):
            raise FilePolicyError(f"{field} must be inside MCP data directory: {self.root}")
        self.root.mkdir(parents=True, exist_ok=True)
        return str(path)

    def _rewrite_json(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: self.resolve(item, key) if key in EMBEDDED_FILE_KEYS and isinstance(item, str)
                else self._rewrite_json(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._rewrite_json(item) for item in value]
        return value

    def prepare(self, arguments: dict[str, Any]) -> dict[str, Any]:
        prepared = dict(arguments)
        for name, value in prepared.items():
            if name.endswith("_file") and isinstance(value, str):
                path = self.resolve(value, name)
                prepared[name] = path
                if name == "input_file" and Path(path).is_file():
                    if Path(path).stat().st_size > MAX_JSON_FILE_BYTES:
                        raise FilePolicyError("input_file exceeds the 8 MB limit")
                    try:
                        decoded = json.loads(Path(path).read_text(encoding="utf-8"))
                    except (OSError, UnicodeError, json.JSONDecodeError):
                        continue  # The CLI will report the malformed input.
                    if self._rewrite_json(decoded) != decoded:
                        raise FilePolicyError(
                            "paths inside input_file must be absolute paths inside the MCP data directory"
                        )
            elif name in {"input", "state"} and isinstance(value, str):
                try:
                    decoded = json.loads(value)
                except json.JSONDecodeError:
                    continue  # The CLI will return its normal invalid-JSON error.
                rewritten = self._rewrite_json(decoded)
                if rewritten != decoded:
                    prepared[name] = json.dumps(rewritten, ensure_ascii=False, separators=(",", ":"))
        return prepared
