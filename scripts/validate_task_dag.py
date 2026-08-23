#!/usr/bin/env python3
"""Validate task DAG: acyclicity, well-formedness, and sync.

Usage:
    uv run python scripts/validate_task_dag.py [tasks-file]

Exit codes:
    0 - all checks pass
    1 - one or more checks fail
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_tasks(path: Path) -> list[dict]:
    """Load tasks from a JSON task DAG file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("tasks", [])


def check_well_formed(tasks: list[dict]) -> list[str]:
    """Check that every task has required fields."""
    failures: list[str] = []
    required_fields = ["task_id", "title", "status", "dependencies", "requirements", "acceptance_criteria"]
    for task in tasks:
        task_id = task.get("task_id", "<unknown>")
        for field in required_fields:
            if field not in task:
                failures.append(f"{task_id} missing required field: {field}")
        if not task.get("task_id"):
            failures.append("Task with empty task_id found")
    return failures


def check_acyclic(tasks: list[dict]) -> list[str]:
    """Check that the dependency graph is acyclic using DFS."""
    failures: list[str] = []

    graph: dict[str, list[str]] = {}
    for task in tasks:
        tid = task.get("task_id")
        if tid:
            graph[tid] = task.get("dependencies", [])

    # DFS cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = dict.fromkeys(graph, 0)

    def dfs(node: str, path: list[str]) -> bool:
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycle = [*path[cycle_start:], neighbor]
                failures.append(f"Cycle detected: {' -> '.join(cycle)}")
                return True
            if color[neighbor] == WHITE and dfs(neighbor, path):
                return True
        path.pop()
        color[node] = BLACK
        return False

    for tid in list(graph):
        if color[tid] == WHITE:
            dfs(tid, [])

    return failures


def check_sync(docs_path: Path, runner_path: Path) -> list[str]:
    """Check that docs/tasks and .github/task-runner are in sync."""
    failures: list[str] = []
    if not docs_path.exists():
        return failures
    if not runner_path.exists():
        failures.append(f"Runner file missing: {runner_path}")
        return failures
    docs_data = json.loads(docs_path.read_text(encoding="utf-8"))
    runner_data = json.loads(runner_path.read_text(encoding="utf-8"))
    docs_tasks = {t["task_id"]: t for t in docs_data.get("tasks", [])}
    runner_tasks = {t["task_id"]: t for t in runner_data.get("tasks", [])}
    if set(docs_tasks) != set(runner_tasks):
        missing_in_runner = set(docs_tasks) - set(runner_tasks)
        missing_in_docs = set(runner_tasks) - set(docs_tasks)
        if missing_in_runner:
            failures.append(f"Tasks missing in runner: {sorted(missing_in_runner)}")
        if missing_in_docs:
            failures.append(f"Tasks missing in docs: {sorted(missing_in_docs)}")
    for tid in set(docs_tasks) & set(runner_tasks):
        if docs_tasks[tid].get("status") != runner_tasks[tid].get("status"):
            failures.append(f"{tid} status mismatch: docs={docs_tasks[tid].get('status')} runner={runner_tasks[tid].get('status')}")
    return failures


def main() -> int:
    tasks_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".github/task-runner/tasks.json")
    failures: list[str] = []

    if not tasks_path.exists():
        print(f"Tasks file not found: {tasks_path}")
        return 1

    tasks = load_tasks(tasks_path)

    failures.extend(check_well_formed(tasks))
    failures.extend(check_acyclic(tasks))

    # Check sync between docs and runner

    runner_path = Path(".github/task-runner/tasks.json")
    if tasks_path != runner_path:
        failures.extend(check_sync(tasks_path, runner_path))

    if failures:
        print("Task DAG validation FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"Task DAG validation PASSED: {len(tasks)} tasks, acyclic, well-formed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
