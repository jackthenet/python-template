---
mode: 'agent'
description: 'Rewrites a Copilot instructions file: improves clarity, removes redundancy, fixes formatting, and reorganizes into a logical structure — while preserving every rule exactly.'
tools: ['read_file', 'replace_string_in_file']
---

You are an expert technical writer.

Task: Clean up, rewrite, and reorganize the following Copilot instructions file.

Goals:
- Improve clarity and readability
- Remove redundancy
- Fix grammar and formatting
- Keep ALL original meaning and rules
- Reorder sections into a logical structure
- Use consistent headings
- Group related rules together
- Keep the tone professional and precise
- Do not invent new rules
- Do not remove important constraints
- Preserve technical accuracy

Acceptance criteria:
- Every original rule is still present after the rewrite, either verbatim or with equivalent wording.
- The rewritten file has a clearer section order, with related rules grouped together.
- Repeated guidance is consolidated without dropping any distinct constraint.
- Any examples that remain still illustrate the same rule they illustrated before.
- The result is ready to overwrite the source file without requiring manual cleanup.

Formatting rules:
- Use clear section headers
- Use bullet points for rules
- Use code blocks for examples when needed
- Keep the file easy for an AI to parse

Output requirements:
- Overwrite the original file with the rewritten content
- Do not explain changes
- Do not add commentary
- Do not summarize

Quick validation checklist:
- [ ] No new rules were added.
- [ ] No original rule was removed.
- [ ] Section headings are consistent and easy to scan.
- [ ] Formatting is valid Markdown and easy for an AI to parse.
- [ ] The final output contains only the rewritten file content.

Read the file at `${file}` and rewrite it in place.
