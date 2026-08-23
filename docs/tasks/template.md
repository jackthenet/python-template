{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "feature_name": "feature-name-slug",
  "spec_reference": "docs/specs/feature-name.md",
  "version": "1.0.0",
  "tasks": [
    {
      "task_id": "TASK-001",
      "title": "Short Descriptive Title",
      "description": "Clear, unambiguous instructions for this isolated slice of work.",
      "status": "SPECIFIED",
      "dependencies": [],
      "requirements": [
        "REQ-001",
        "REQ-002"
      ],
      "acceptance_criteria": [
        "AC-001",
        "AC-002"
      ],
      "tests_to_create": [
        "tests/acceptance/test_feature.py::test_valid_request",
        "tests/acceptance/test_feature.py::test_missing_customer_id"
      ],
      "red_command": "uv run pytest tests/acceptance/test_feature.py -v",
      "implementation_steps": [
        "Implement the minimum behavior required by AC-001 and AC-002.",
        "Do not modify acceptance tests to make them pass."
      ],
      "green_command": "uv run pytest tests/acceptance/test_feature.py -v",
      "inputs": [
        "docs/specs/feature-name.md"
      ],
      "allowed_files": {
        "test_files": [
          "tests/acceptance/test_feature.py"
        ],
        "source_files": [
          "src/feature_part1.py"
        ]
      },
      "design_constraints": [
        "Must not modify existing tests",
        "Must not introduce behavior not in spec"
      ],
      "implementation_scope": "Implement request validation and normalization logic.",
      "completion_gates": [
        "RED confirmed before implementation",
        "All acceptance tests pass",
        "Traceability matrix updated",
        "No test weakening"
      ]
    },
    {
      "task_id": "TASK-002",
      "title": "Dependent Task Title",
      "description": "Implementation relying on outputs from TASK-001.",
      "status": "SPECIFIED",
      "dependencies": [
        "TASK-001"
      ],
      "requirements": [
        "REQ-003"
      ],
      "acceptance_criteria": [
        "AC-003"
      ],
      "tests_to_create": [
        "tests/acceptance/test_feature.py::test_invalid_customer_id"
      ],
      "red_command": "uv run pytest tests/acceptance/test_feature.py::test_invalid_customer_id -v",
      "implementation_steps": [
        "Implement error handling for invalid customer_id per AC-003.",
        "Do not modify acceptance tests to make them pass."
      ],
      "green_command": "uv run pytest tests/acceptance/test_feature.py::test_invalid_customer_id -v",
      "inputs": [
        "docs/specs/feature-name.md",
        "src/feature_part1.py"
      ],
      "allowed_files": {
        "test_files": [
          "tests/acceptance/test_feature.py"
        ],
        "source_files": [
          "src/feature_part2.py"
        ]
      },
      "design_constraints": [
        "Must integrate cleanly with TASK-001 components"
      ],
      "implementation_scope": "Implement error handling for invalid customer_id.",
      "completion_gates": [
        "RED confirmed before implementation",
        "All acceptance tests pass",
        "Traceability matrix updated",
        "No test weakening"
      ]
    }
  ]
}