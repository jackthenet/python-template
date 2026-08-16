"""PostToolUse hook: run Ruff on Python files changed by supported edit tools.

Reads the hook JSON payload from stdin, extracts file paths from known
file-editing tool calls, and runs Ruff on those paths.
If ruff reports issues it injects a systemMessage so the agent sees them
immediately and can fix them before moving on.

Exit codes:
  0  — no issues (or not a file-edit tool call)
  1  — ruff found issues (non-blocking; systemMessage is returned)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import orjson

# Tools that edit files (programmatic Copilot tool names).
_FILE_EDIT_TOOLS = frozenset(
    [
        "apply_patch",
        "create_file",
        "functions.apply_patch",
        "replace_string_in_file",
        "multi_replace_string_in_file",
    ]
)

_PATCH_FILE_PATTERN = re.compile(r"^\*\*\* (?:Add|Update) File: (.+)$", re.MULTILINE)


def _collect_patch_paths(patch_text: str) -> list[str]:
    """Extract Python file paths from an apply_patch payload."""

    paths: list[str] = []

    for raw_path in _PATCH_FILE_PATTERN.findall(patch_text):
        file_path = raw_path.split(" -> ", 1)[0].strip()
        if file_path.endswith(".py"):
            paths.append(file_path)

    return paths


def _collect_py_paths(tool_name: str, tool_input: dict) -> list[str]:
    """Return Python file paths affected by the tool call."""
    paths: list[str] = []

    if tool_name in {"apply_patch", "functions.apply_patch"}:
        paths.extend(_collect_patch_paths(str(tool_input.get("input", ""))))
    elif tool_name == "multi_replace_string_in_file":
        for replacement in tool_input.get("replacements", []):
            p = replacement.get("filePath", "")
            if p.endswith(".py"):
                paths.append(p)
    else:
        p = tool_input.get("filePath", "")
        if p.endswith(".py"):
            paths.append(p)

    # Filter to files that exist and deduplicate while preserving order.
    deduped_paths: list[str] = []
    seen_paths: set[str] = set()

    for path in paths:
        if path in seen_paths:
            continue
        seen_paths.add(path)
        if Path(path).exists():
            deduped_paths.append(path)

    return deduped_paths


def main() -> None:
    try:
        payload = orjson.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    tool_name: str = payload.get("tool_name", payload.get("tool", ""))
    if tool_name not in _FILE_EDIT_TOOLS:
        sys.exit(0)

    tool_input: dict = payload.get("tool_input", payload.get("toolInput", {}))
    paths = _collect_py_paths(tool_name, tool_input)
    if not paths:
        sys.exit(0)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--output-format",
            "concise",
            *paths,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        sys.exit(0)

    issues = (result.stdout or result.stderr).strip()
    print(orjson.dumps({"systemMessage": f"ruff found issues after edit:\n{issues}"}).decode("utf-8"))
    sys.exit(0)


if __name__ == "__main__":
    main()
