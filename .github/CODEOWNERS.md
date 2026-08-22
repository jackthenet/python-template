# Protect specifications: Requires human review
/docs/specs/              @repository-owners

# Protect test suites: Only QA Agent / Humans should alter tests
/tests/                   @qa-agent-bot

# Source implementation: Target directory for Coder Agent
/src/                     @coder-agent-bot