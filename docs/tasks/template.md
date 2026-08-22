# Task [000]: [Task Title]

## Metadata
- **Status:** [Pending | In Progress | Completed]
- **Spec Reference:** `/docs/specs/[feature-name].md`
- **Prerequisites:** [e.g., Task 001, or None]

## Context & Execution Steps
[Provide direct, unambiguous instructions for this specific slice of work.]

1. Create module at `src/[path/to/file.py]`.
2. Implement components defined in `/docs/specs/[feature-name].md` (Section 3).
3. Ensure error handling follows Section 5 of the spec.

## Work Checklist
- [ ] Implement core logic in target file
- [ ] Add type hints and docstrings
- [ ] Create corresponding unit test file in `tests/`
- [ ] Verify test execution succeeds via verification command

## Verification Command
```bash
# Exact command the AI must run and pass before marking this task as completed
pytest tests/test_[feature].py -v