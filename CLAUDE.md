# CLAUDE.md - Project Rules for LabBot

> This document defines HOW Claude Code should work on LabBot.
> Read at the start of every session to maintain consistency.

## Core Operating Principles

### 1. Single Session Execution
- ✅ Complete the ENTIRE subtask in this session
- ✅ End every session with a git commit
- ❌ If blocked, document why and mark as BLOCKED

### 2. Read Before Acting
**Every session must begin with:**
1. Read DEVELOPMENT_PLAN.md completely
2. Locate the specific subtask ID from the prompt
3. Verify prerequisites are marked `[x]` complete
4. Read completion notes from prerequisites for context

### 3. File Management

**Project Structure:**
```
labbot/
├── src/
│   └── labbot/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── config.py            # Settings
│       ├── logging_config.py    # Centralized logging
│       ├── schemas.py           # Pydantic models
│       ├── pii_detector.py      # PII detection
│       ├── interpreter.py       # Claude API integration
│       ├── citations.py         # Medical citations
│       └── static/              # Frontend files
│           ├── index.html
│           ├── styles.css
│           └── app.js
├── tests/
│   ├── __init__.py
│   ├── test_*.py
│   └── fixtures/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── template.yaml               # SAM template
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── DEVELOPMENT_PLAN.md
├── PROJECT_BRIEF.md
└── DEVLOG.md                   # Development journey log
```

**Creating Files:**
- Use exact paths specified in subtask
- Add proper module docstrings
- Include type hints on all functions
- Never use single-letter variable names

**Modifying Files:**
- Only modify files listed in subtask
- Preserve existing functionality
- Update related tests

### 4. Testing Requirements

**Testing Philosophy:**
- Prioritize integration testing over heavily mocked unit tests
- Test real interactions between components
- Only mock external dependencies (Claude API) when necessary
- Test the actual code paths users will use

**Running Tests:**
```bash
# All tests with coverage
pytest tests/ -v --cov=labbot --cov-report=term-missing

# Specific test file
pytest tests/test_interpreter.py -v

# Integration tests only
pytest tests/ -v -m integration
```

**Before Every Commit:**
- [ ] All tests pass
- [ ] Coverage >80%
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Type checking passes: `mypy src/`

### 5. Process Documentation

> **CRITICAL FOR SHOWCASE PROJECT**: This project demonstrates the DevPlan methodology.
> Every development decision should be documented for the journey story.

**DEVLOG.md Requirements:**
- Timestamp each entry
- Document key decisions and why
- Note any deviations from the plan
- Record time spent on each phase
- Capture "aha moments" and challenges

**DEVLOG Entry Format:**
```markdown
## [YYYY-MM-DD HH:MM] Subtask X.Y.Z: Title

**Time Spent**: X minutes

**What Was Done**:
- Brief description of implementation

**Key Decisions**:
- Why we chose X over Y

**Challenges**:
- What was harder than expected

**Learnings**:
- What would we do differently
```

**Commit Messages for Story:**
- Be descriptive - these become the git log narrative
- Reference subtask IDs
- Explain the "why" not just the "what"

### 6. Completion Protocol

**When a subtask is complete:**

1. **Update DEVELOPMENT_PLAN.md** with completion notes:
```markdown
**Completion Notes:**
- **Implementation**: Brief description of what was built
- **Files Created**:
  - `src/labbot/parser.py` - 234 lines
  - `tests/test_parser.py` - 156 lines
- **Files Modified**:
  - `src/labbot/__init__.py` - added parser import
- **Tests**: 12 unit tests, 85% coverage
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/X.Y-description
- **Notes**: Any deviations, issues, or future work
```

2. **Update DEVLOG.md** with journey entry

3. **Check all checkboxes** in the subtask

4. **Git commit** with semantic message:
```bash
git add .
git commit -m "feat(interpreter): implement Claude API integration [3.1.1]

- Added anthropic client with Haiku model
- Created interpretation prompt template
- Structured output parsing to InterpretationResponse
- 90% coverage on interpreter module

Time: 45 minutes"
```

5. **Report completion** with summary

### 7. Technology Stack

**Backend:**
- Python 3.11+
- FastAPI 0.109+
- Pydantic 2.6+
- anthropic 0.18+
- mangum 0.17+ (Lambda adapter)

**Testing:**
- pytest 7.4+
- pytest-cov 4.1+
- pytest-asyncio 0.23+
- httpx 0.26+ (async test client)

**Quality:**
- ruff 0.2+
- mypy 1.8+

**Deployment:**
- AWS SAM
- GitHub Actions

**Installing Dependencies:**
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### 8. Error Handling

**If you encounter an error:**
1. Attempt to fix using project patterns
2. If blocked, update DEVELOPMENT_PLAN.md:
   ```markdown
   **Completion Notes:**
   - **Status**: ❌ BLOCKED
   - **Error**: [Detailed error message]
   - **Attempted**: [What was tried]
   - **Root Cause**: [Analysis]
   - **Suggested Fix**: [What should be done]
   ```
3. Update DEVLOG.md with the blocker
4. Do NOT mark subtask complete if blocked
5. Do NOT commit broken code
6. Report immediately

### 9. Code Quality Standards

**Python Style:**
- Follow PEP 8
- Type hints on all functions: `def func(param: str) -> dict[str, Any]:`
- Docstrings: Google style
- Max line length: 100 characters
- Use `ruff` for linting
- Use `mypy` for type checking

**Naming:**
- Never use single-letter variable names
- Descriptive names: `lab_value` not `lv`
- Constants: `UPPER_SNAKE_CASE`
- Classes: `PascalCase`
- Functions/variables: `snake_case`

**Example Function:**
```python
def detect_pii(input_text: str) -> list[str]:
    """Detect personally identifiable information in text.

    Args:
        input_text: The text to scan for PII patterns.

    Returns:
        List of PII types detected (e.g., ["ssn", "email"]).
        Empty list if no PII found.

    Example:
        >>> detect_pii("SSN: 123-45-6789")
        ["ssn"]
        >>> detect_pii("Hemoglobin: 14.5 g/dL")
        []
    """
    detected_types: list[str] = []
    # Implementation...
    return detected_types
```

**Imports:**
```python
# Standard library
import logging
import re
from typing import Any

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local
from labbot.config import settings
from labbot.schemas import LabResultsInput
```

**Prohibited:**
- `print()` for output (use logging)
- `exit()` (raise exceptions instead)
- Bare `except:` (catch specific exceptions)
- Single-letter variable names
- Commented-out code in commits

### 10. Build Verification

**Before marking subtask complete:**

```bash
# Activate virtual environment
source .venv/bin/activate

# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Tests with coverage
pytest tests/ -v --cov=labbot --cov-report=term-missing

# Verify app starts
uvicorn labbot.main:app --reload &
curl http://localhost:8000/health
```

**All must pass with no errors.**

## Checklist: Starting a New Session

- [ ] Activate virtual environment: `source .venv/bin/activate`
- [ ] Read DEVELOPMENT_PLAN.md completely
- [ ] Read DEVLOG.md for context
- [ ] Locate subtask ID from prompt
- [ ] Verify prerequisites marked `[x]`
- [ ] Read prerequisite completion notes
- [ ] Understand success criteria
- [ ] Note start time for DEVLOG
- [ ] Ready to code!

## Checklist: Ending a Session

- [ ] All subtask checkboxes checked
- [ ] All tests pass (pytest)
- [ ] Linting clean (ruff)
- [ ] Type checking clean (mypy)
- [ ] Completion notes written in DEVELOPMENT_PLAN.md
- [ ] DEVLOG.md entry added with time and learnings
- [ ] Git commit with semantic message and subtask ID
- [ ] User notified

---

**Version**: 1.0
**Last Updated**: 2025-12-19
**Project**: LabBot

*Generated by DevPlan methodology*
