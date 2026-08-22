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
      "status": "pending",
      "dependencies": [],
      "inputs": [
        "docs/specs/feature-name.md"
      ],
      "allowed_files": {
        "test_files": [
          "tests/test_feature_part1.py"
        ],
        "source_files": [
          "src/feature_part1.py"
        ]
      },
      "acceptance_criteria": [
        "Criterion 1: Specific input yields expected output",
        "Criterion 2: Raises specific Exception on invalid input"
      ],
      "verification_command": "pytest tests/test_feature_part1.py -v"
    },
    {
      "task_id": "TASK-002",
      "title": "Dependent Task Title",
      "description": "Implementation relying on outputs from TASK-001.",
      "status": "pending",
      "dependencies": [
        "TASK-001"
      ],
      "inputs": [
        "docs/specs/feature-name.md",
        "src/feature_part1.py"
      ],
      "allowed_files": {
        "test_files": [
          "tests/test_feature_part2.py"
        ],
        "source_files": [
          "src/feature_part2.py"
        ]
      },
      "acceptance_criteria": [
        "Criterion 1: Integrates with TASK-001 components cleanly"
      ],
      "verification_command": "pytest tests/test_feature_part2.py -v"
    }
  ]
}