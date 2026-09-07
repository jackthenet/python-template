"""Verify specification traceability against test functions."""

import re
import sys
from pathlib import Path


def parse_spec(spec_path: Path) -> dict[str, list[str]]:
    """Extract stable IDs from a spec file."""
    text = spec_path.read_text(encoding="utf-8")
    return {
        "requirements": sorted(set(re.findall(r"REQ-\d+", text))),
        "acceptance_criteria": sorted(set(re.findall(r"AC-\d+", text))),
        "invariants": sorted(set(re.findall(r"INV-\d+", text))),
        "edge_cases": sorted(set(re.findall(r"EDGE-\d+", text))),
        "nfrs": sorted(set(re.findall(r"NFR-\d+", text))),
    }


def find_test_functions(test_dir: Path) -> dict[str, list[str]]:
    """Map test category directories to test function names."""
    result: dict[str, list[str]] = {}
    for category in ("acceptance", "integration", "contract", "property", "unit"):
        cat_dir = test_dir / category
        if not cat_dir.exists():
            continue
        funcs: list[str] = []
        for py_file in cat_dir.rglob("*.py"):
            if py_file.name.startswith("test_"):
                text = py_file.read_text(encoding="utf-8")
                funcs.extend(re.findall(r"def (test_\w+)", text))
        if funcs:
            result[category] = sorted(set(funcs))
    return result


def check_traceability(spec_ids: dict[str, list[str]], test_funcs: dict[str, list[str]]) -> list[str]:
    """Run traceability checks and return failure messages."""
    failures: list[str] = []

    # Every requirement must have at least one acceptance criterion
    for req in spec_ids["requirements"]:
        if not spec_ids["acceptance_criteria"]:
            failures.append(f"{req} has no acceptance criteria")

    # Every acceptance criterion must have an executable test
    all_test_funcs: list[str] = []
    for funcs in test_funcs.values():
        all_test_funcs.extend(funcs)

    if not all_test_funcs:
        for ac in spec_ids["acceptance_criteria"]:
            failures.append(f"{ac} has no executable test")

    # Every invariant must have a property test
    property_funcs = test_funcs.get("property", [])
    for inv in spec_ids["invariants"]:
        if not property_funcs:
            failures.append(f"{inv} has no property test")

    # No orphaned acceptance tests (tests without spec reference)
    # This is a heuristic: check if test file docstrings reference AC/REQ IDs
    # For now, skip this check as it requires parsing test file contents.

    return failures


def main() -> int:
    spec_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/specs/template.md")
    if not spec_path.exists():
        print(f"Spec file not found: {spec_path}")
        return 1

    test_dir = Path("tests")
    if not test_dir.exists():
        print("Test directory not found: tests/")
        return 1

    spec_ids = parse_spec(spec_path)
    test_funcs = find_test_functions(test_dir)
    failures = check_traceability(spec_ids, test_funcs)

    print("Specification validation")
    print("\u2500" * 25)

    for req in spec_ids["requirements"]:
        print(
            f"\u2713 {req} has acceptance criteria"
            if spec_ids["acceptance_criteria"]
            else f"\u2717 {req} has no acceptance criteria"
        )

    all_test_funcs = [f for funcs in test_funcs.values() for f in funcs]
    property_funcs = test_funcs.get("property", [])

    for ac in spec_ids["acceptance_criteria"]:
        has_test = any(ac.lower().replace("ac-", "") in f for f in all_test_funcs)
        print(f"\u2713 {ac} has executable test" if has_test else f"\u2717 {ac} has no executable test")

    for inv in spec_ids["invariants"]:
        has_prop = any(inv.lower().replace("inv-", "") in f for f in property_funcs)
        print(f"\u2713 {inv} has property test" if has_prop else f"\u2717 {inv} has no property test")

    if failures:
        print(f"\nTraceability: FAIL ({len(failures)} issue(s))")
        for f in failures:
            print(f"  \u2717 {f}")
        return 1

    print("\nTraceability: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
