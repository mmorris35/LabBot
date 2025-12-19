# LabBot - Development Plan

## How to Use This Plan

**For Claude Code**: Read this plan, find the subtask ID from the prompt, complete ALL checkboxes, update completion notes, commit.

**For You**: Use this prompt (change only the subtask ID):
```
please re-read CLAUDE.md and DEVELOPMENT_PLAN.md (the entire documents, for context), then continue with [X.Y.Z], following all of the development plan and CLAUDE.md rules.
```

---

## Project Overview

**Project Name**: LabBot
**Goal**: Help patients interpret their lab results in plain language
**Target Users**: Patients with medical lab results, Caregivers, Health-conscious individuals
**Timeline**: 1 week

**MVP Scope**:
- [ ] Accept JSON lab results via web form or API endpoint
- [ ] PII detection gate - refuse AI analysis if personal identifiers detected
- [ ] Plain-language explanations with citations for each lab value
- [ ] Flag abnormal values with severity indicators
- [ ] Simple responsive web UI for input and results display

---

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI**: Claude API (Haiku)
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Linting**: ruff
- **Type Checking**: mypy
- **Deployment**: AWS Lambda + API Gateway via SAM
- **CI/CD**: GitHub Actions
- **Frontend**: HTML/CSS/vanilla JS

---

## Progress Tracking

### Phase 0: Foundation
- [ ] 0.1.1: Initialize Git Repository
- [ ] 0.1.2: Python Project Setup
- [ ] 0.2.1: Linting and Type Checking
- [ ] 0.2.2: CI/CD Pipeline

### Phase 1: Core API
- [ ] 1.1.1: FastAPI Application Structure
- [ ] 1.1.2: Health Check Endpoint
- [ ] 1.2.1: Lab Results Schema
- [ ] 1.2.2: Input Validation Endpoint

### Phase 2: PII Detection
- [ ] 2.1.1: PII Detection Module
- [ ] 2.1.2: PII Gate Middleware

### Phase 3: AI Interpretation
- [ ] 3.1.1: Claude API Integration
- [ ] 3.1.2: Lab Value Interpreter
- [ ] 3.1.3: Citation Generator

### Phase 4: Web Frontend
- [ ] 4.1.1: Static HTML/CSS/JS Frontend
- [ ] 4.1.2: API Integration
- [ ] 4.1.3: Results Display

### Phase 5: AWS Deployment
- [ ] 5.1.1: SAM Template
- [ ] 5.1.2: GitHub Actions Deployment
- [ ] 5.1.3: End-to-End Verification

**Current**: Phase 0
**Next**: 0.1.1

---

## Phase 0: Foundation

**Goal**: Set up repository, project structure, and development tools
**Duration**: Day 1

### Task 0.1: Repository Setup

**Git**: Create branch `feature/0.1-repository-setup` when starting first subtask. Commit after each subtask. Squash merge to main when task complete.

---

**Subtask 0.1.1: Initialize Git Repository (Single Session)**

**Prerequisites**:
- None (first subtask)

**Deliverables**:
- [ ] Run `git init` to initialize repository
- [ ] Create `.gitignore` with Python ignores
- [ ] Create `README.md` with project name and description
- [ ] Create `LICENSE` file with GNU GPL text
- [ ] Run `git add .` and `git commit -m 'chore: initial repository setup'`

**Technology Decisions**:
- Use GNU GPL license per user preference
- Follow semantic commit convention

**Files to Create**:
- `.gitignore`
- `README.md`
- `LICENSE`

**Success Criteria**:
- [ ] `.gitignore` includes `__pycache__/`, `.venv/`, `.env`, `*.pyc`, `.mypy_cache/`, `.ruff_cache/`
- [ ] README.md has `# LabBot` heading and project description
- [ ] LICENSE file contains GNU GPL license text
- [ ] First commit exists with semantic message
- [ ] `git status` shows clean working tree

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: N/A (no code yet)
- **Build**: N/A
- **Branch**: feature/0.1-repository-setup
- **Notes**: (any additional context)

---

**Subtask 0.1.2: Python Project Setup (Single Session)**

**Prerequisites**:
- [x] 0.1.1: Initialize Git Repository

**Deliverables**:
- [x] Create `pyproject.toml` with project metadata
- [x] Create `src/labbot/__init__.py` with `__version__ = "0.1.0"`
- [x] Create `src/labbot/main.py` with placeholder FastAPI app
- [x] Create `.python-version` with `3.11`
- [x] Create virtual environment: `python -m venv .venv`
- [x] Install dev dependencies: `pip install -e ".[dev]"`
- [x] Verify: `python -c "from labbot import __version__; print(__version__)"`

**Technology Decisions**:
- Use `src/` layout for proper package structure
- Use `pyproject.toml` (modern Python packaging)
- Include dev dependencies: pytest, pytest-cov, pytest-asyncio, ruff, mypy, httpx

**Files to Create**:
- `pyproject.toml`
- `src/labbot/__init__.py`
- `src/labbot/main.py`
- `.python-version`

**pyproject.toml content**:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "labbot"
version = "0.1.0"
description = "Help patients interpret their lab results in plain language"
readme = "README.md"
requires-python = ">=3.11"
license = "GPL-3.0-or-later"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "anthropic>=0.18.0",
    "pydantic>=2.6.0",
    "mangum>=0.17.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/labbot"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Success Criteria**:
- [x] `pip install -e ".[dev]"` completes without errors
- [x] `python -c "from labbot import __version__"` outputs "0.1.0"
- [x] `python -c "from labbot.main import app"` imports without error
- [x] `.venv/` directory exists and is in `.gitignore`

---

**Completion Notes**:
- **Implementation**: Created complete Python project structure with modern packaging setup. Implemented src/labbot package with version marker and placeholder FastAPI application. Configured pyproject.toml with all dependencies and development tools (pytest, ruff, mypy). Created and activated virtual environment with all dependencies installed successfully.
- **Files Created**:
  - `pyproject.toml` - 47 lines
  - `src/labbot/__init__.py` - 3 lines
  - `src/labbot/main.py` - 26 lines
  - `.python-version` - 1 line
  - `tests/__init__.py` - 0 lines (created for linting)
- **Files Modified**: None
- **Tests**: N/A (no code tests for infrastructure setup)
- **Build**: pip install success, ruff pass, mypy pass
- **Branch**: feature/0.1-repository-setup
- **Notes**: Used Python 3.12 (compatible with >=3.11 requirement). All verification checks passed: imports work, TestClient successful, linting clean. Virtual environment properly created and configured.

---

### Task 0.1 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/0.1-repository-setup`
- [ ] Commit: `git commit -m "feat: repository and project setup"`
- [ ] Delete branch: `git branch -d feature/0.1-repository-setup`

---

### Task 0.2: Development Tools

**Git**: Create branch `feature/0.2-development-tools` when starting first subtask.

---

**Subtask 0.2.1: Linting and Type Checking (Single Session)**

**Prerequisites**:
- [x] 0.1.2: Python Project Setup

**Deliverables**:
- [x] Verify ruff is configured in `pyproject.toml`
- [x] Verify mypy is configured in `pyproject.toml`
- [x] Run `ruff check src/` - should pass
- [x] Run `mypy src/` - should pass
- [x] Create `tests/__init__.py`
- [x] Create `tests/test_version.py` with version test

**Files to Create**:
- `tests/__init__.py`
- `tests/test_version.py`

**test_version.py content**:
```python
"""Test package version."""

from labbot import __version__


def test_version_exists() -> None:
    """Verify version string is set."""
    assert __version__ == "0.1.0"
```

**Success Criteria**:
- [x] `ruff check src/ tests/` exits with code 0
- [x] `mypy src/` exits with code 0
- [x] `pytest tests/ -v` passes with 1 test

---

**Completion Notes**:
- **Implementation**: Verified ruff and mypy are properly configured in pyproject.toml with correct rules (E, F, I, N, W, UP for ruff; strict mode for mypy). Created tests/__init__.py and tests/test_version.py with a simple version verification test. All linting, type checking, and test verification passed successfully.
- **Files Created**:
  - `tests/test_version.py` - 6 lines
- **Files Modified**: None
- **Tests**: 1 test (test_version_exists), 100% coverage
- **Build**: ruff: pass (all checks passed), mypy: pass (no issues found)
- **Branch**: feature/0.2-development-tools
- **Notes**: tests/__init__.py already existed from 0.1.2 setup. All verification commands executed successfully: ruff check src/ tests/ (All checks passed!), mypy src/ (Success: no issues found in 2 source files), pytest tests/test_version.py -v (1 passed).

---

**Subtask 0.2.2: CI/CD Pipeline (Single Session)**

**Prerequisites**:
- [x] 0.2.1: Linting and Type Checking

**Deliverables**:
- [x] Create `.github/workflows/ci.yml`
- [x] Define jobs: lint, typecheck, test
- [x] Configure triggers: push to main, pull_request
- [x] Add CI status badge to README.md

**ci.yml content**:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - run: ruff check src/ tests/

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install mypy
      - run: mypy src/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --cov=labbot --cov-report=term-missing
```

**Success Criteria**:
- [x] `.github/workflows/ci.yml` has valid YAML syntax
- [x] README has CI badge: `![CI](https://github.com/mmn/labbot/actions/workflows/ci.yml/badge.svg)`
- [x] Workflow would run lint, typecheck, and test jobs

---

**Completion Notes**:
- **Implementation**: Created GitHub Actions CI/CD workflow with three parallel jobs (lint, typecheck, test). The workflow is triggered on push to main and pull requests. Updated README.md with correct CI badge URL pointing to the workflow.
- **Files Created**:
  - `.github/workflows/ci.yml` - 38 lines
- **Files Modified**:
  - `README.md` - updated badge URL from USER placeholder to mmn
- **Tests**: N/A (CI config - validated through existing test suite)
- **Build**: YAML valid (confirmed via Python YAML parser), ruff: pass, mypy: pass, pytest: pass (1/1 tests)
- **Branch**: feature/0.2-development-tools
- **Notes**: Workflow defines three independent jobs that will run in parallel: lint (ruff check), typecheck (mypy), and test (pytest with coverage). All prerequisites met. Ready for squash merge to main.

---

### Task 0.2 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/0.2-development-tools`
- [ ] Commit: `git commit -m "feat: add linting, type checking, and CI pipeline"`
- [ ] Delete branch: `git branch -d feature/0.2-development-tools`

---

## Phase 1: Core API

**Goal**: Set up FastAPI application with input validation
**Duration**: Day 2

### Task 1.1: FastAPI Application

**Git**: Create branch `feature/1.1-fastapi-app` when starting first subtask.

---

**Subtask 1.1.1: FastAPI Application Structure (Single Session)**

**Prerequisites**:
- [x] 0.2.2: CI/CD Pipeline

**Deliverables**:
- [x] Update `src/labbot/main.py` with proper FastAPI app
- [x] Create `src/labbot/config.py` for settings
- [x] Create `src/labbot/logging_config.py` for centralized logging
- [x] Add CORS middleware for frontend
- [x] Add medical disclaimer in app metadata

**main.py structure**:
```python
"""LabBot FastAPI application."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from labbot.config import settings
from labbot.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

MEDICAL_DISCLAIMER = """
DISCLAIMER: LabBot provides educational information only and is not a substitute 
for professional medical advice, diagnosis, or treatment. Always consult with a 
qualified healthcare provider about your lab results.
"""

app = FastAPI(
    title="LabBot",
    description=f"Lab results interpreter API.\n\n{MEDICAL_DISCLAIMER}",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {"message": "LabBot API", "version": "0.1.0"}
```

**Success Criteria**:
- [x] `uvicorn labbot.main:app --reload` starts server
- [x] GET `/` returns JSON with message and version
- [x] CORS headers present in responses
- [x] Logging outputs to console with proper format

---

**Completion Notes**:
- **Implementation**: Implemented complete FastAPI application structure with centralized configuration and logging. Created Settings class for environment-based configuration, setup_logging function for structured logging, and updated main.py to use both with proper CORS middleware and medical disclaimer in app metadata.
- **Files Created**:
  - `src/labbot/config.py` - 60 lines (Settings class with CORS, API keys, logging, and app configuration)
  - `src/labbot/logging_config.py` - 57 lines (Centralized logging setup with dictConfig)
  - `tests/test_config.py` - 89 lines (7 tests for Settings class)
  - `tests/test_main.py` - 53 lines (4 tests for FastAPI app)
  - `tests/test_logging_config.py` - 56 lines (5 tests for logging setup)
- **Files Modified**:
  - `src/labbot/main.py` - Updated to use config and logging modules with medical disclaimer
- **Tests**: 16 new tests, 100% coverage on all modules
- **Build**: ruff: pass, mypy: pass, pytest: 17/17 pass
- **Branch**: feature/1.1-fastapi-app
- **Notes**: All deliverables completed successfully. Settings class uses environment variables (ANTHROPIC_API_KEY, LOG_LEVEL) for flexibility. CORS configured for local development with both localhost:3000, localhost:8000, and 127.0.0.1 variants. Medical disclaimer properly embedded in FastAPI app metadata and visible in auto-generated OpenAPI docs. Logging is initialized at module import time, showing configuration messages. All quality checks (ruff, mypy, pytest with coverage) pass with no issues.

---

**Subtask 1.1.2: Health Check Endpoint (Single Session)**

**Prerequisites**:
- [x] 1.1.1: FastAPI Application Structure

**Deliverables**:
- [x] Add `/health` endpoint returning status
- [x] Create `tests/test_api.py` with endpoint tests
- [x] Test both `/` and `/health` endpoints

**test_api.py content**:
```python
"""Test API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from labbot.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_root(client: AsyncClient) -> None:
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "LabBot API"
    assert "version" in data


async def test_health(client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

**Success Criteria**:
- [x] GET `/health` returns `{"status": "healthy"}`
- [x] All tests pass with pytest
- [x] Coverage > 80% on main.py

---

**Completion Notes**:
- **Implementation**: Added `/health` endpoint to FastAPI application returning `{"status": "healthy"}`. Created comprehensive test suite in `tests/test_api.py` with fixtures and tests for both root and health endpoints.
- **Files Created**:
  - `tests/test_api.py` - 24 lines
- **Files Modified**:
  - `src/labbot/main.py` - added health endpoint (5 lines)
- **Tests**: 2 new tests (test_root, test_health) + 17 existing tests = 19 total, 100% coverage on main.py
- **Build**: ruff: pass, mypy: pass, pytest: 19/19 pass
- **Branch**: feature/1.1-fastapi-app
- **Notes**: All success criteria met. Health endpoint properly returns JSON with "status": "healthy". Both endpoints fully tested with async test client. Coverage exceeds 80% requirement (achieved 100% on main.py). All existing tests continue to pass.

---

### Task 1.1 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/1.1-fastapi-app`
- [ ] Commit: `git commit -m "feat: FastAPI application with health check"`
- [ ] Delete branch: `git branch -d feature/1.1-fastapi-app`

---

### Task 1.2: Lab Results Schema

**Git**: Create branch `feature/1.2-lab-schema` when starting first subtask.

---

**Subtask 1.2.1: Lab Results Schema (Single Session)**

**Prerequisites**:
- [x] 1.1.2: Health Check Endpoint

**Deliverables**:
- [ ] Create `src/labbot/schemas.py` with Pydantic models
- [ ] Define `LabValue` model (name, value, unit, reference_range)
- [ ] Define `LabResultsInput` model (list of LabValue)
- [ ] Define `InterpretedResult` model (for responses)
- [ ] Create `tests/test_schemas.py` with validation tests

**schemas.py structure**:
```python
"""Pydantic schemas for lab results."""

from pydantic import BaseModel, Field


class LabValue(BaseModel):
    """Single lab test value."""
    
    name: str = Field(..., description="Name of the lab test", examples=["Hemoglobin"])
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Unit of measurement", examples=["g/dL"])
    reference_min: float | None = Field(None, description="Minimum reference range")
    reference_max: float | None = Field(None, description="Maximum reference range")


class LabResultsInput(BaseModel):
    """Input payload for lab interpretation."""
    
    lab_values: list[LabValue] = Field(
        ..., 
        description="List of lab values to interpret",
        min_length=1,
        max_length=50,
    )


class SeverityLevel(str, Enum):
    """Severity level for abnormal values."""
    
    NORMAL = "normal"
    BORDERLINE = "borderline"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"


class InterpretedValue(BaseModel):
    """Single interpreted lab value."""
    
    name: str
    value: float
    unit: str
    severity: SeverityLevel
    explanation: str
    citation: str | None = None


class InterpretationResponse(BaseModel):
    """Full interpretation response."""
    
    results: list[InterpretedValue]
    disclaimer: str
    summary: str | None = None
```

**Success Criteria**:
- [ ] All models have proper type hints
- [ ] Validation rejects invalid inputs
- [ ] Tests cover valid and invalid cases

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: (X tests, Y% coverage)
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/1.2-lab-schema
- **Notes**: (any additional context)

---

**Subtask 1.2.2: Input Validation Endpoint (Single Session)**

**Prerequisites**:
- [x] 1.2.1: Lab Results Schema

**Deliverables**:
- [ ] Add POST `/api/interpret` endpoint (stub)
- [ ] Validate input against `LabResultsInput` schema
- [ ] Return 422 for invalid input with details
- [ ] Add tests for validation

**Success Criteria**:
- [ ] Valid JSON accepted, returns 200
- [ ] Invalid JSON returns 422 with errors
- [ ] Missing fields return 422 with field names

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: (X tests, Y% coverage)
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/1.2-lab-schema
- **Notes**: (any additional context)

---

### Task 1.2 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/1.2-lab-schema`
- [ ] Commit: `git commit -m "feat: lab results schema and validation"`
- [ ] Delete branch: `git branch -d feature/1.2-lab-schema`

---

## Phase 2: PII Detection

**Goal**: Implement PII detection to prevent sensitive data from reaching Claude API
**Duration**: Day 2-3

### Task 2.1: PII Detection Module

**Git**: Create branch `feature/2.1-pii-detection` when starting first subtask.

---

**Subtask 2.1.1: PII Detection Module (Single Session)**

**Prerequisites**:
- [x] 1.2.2: Input Validation Endpoint

**Deliverables**:
- [ ] Create `src/labbot/pii_detector.py`
- [ ] Detect: SSN, phone, email, DOB patterns, names (common patterns)
- [ ] Return list of detected PII types
- [ ] Create `tests/test_pii_detector.py` with comprehensive tests

**Detection patterns**:
- SSN: `\d{3}-\d{2}-\d{4}` or `\d{9}`
- Phone: `\d{3}[-.\s]?\d{3}[-.\s]?\d{4}`
- Email: standard email regex
- DOB: `\d{1,2}/\d{1,2}/\d{2,4}` and variations
- Names: Check for common name fields (patient_name, name, full_name)

**Success Criteria**:
- [ ] Detects all PII types listed
- [ ] Returns empty list for clean data
- [ ] Tests cover all pattern types
- [ ] No false positives on numeric lab values

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: (X tests, Y% coverage)
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/2.1-pii-detection
- **Notes**: (any additional context)

---

**Subtask 2.1.2: PII Gate Middleware (Single Session)**

**Prerequisites**:
- [x] 2.1.1: PII Detection Module

**Deliverables**:
- [ ] Integrate PII detector into `/api/interpret` endpoint
- [ ] Return 400 with PII types if detected
- [ ] Add tests for PII rejection
- [ ] Log PII detection events (without logging the PII itself)

**Success Criteria**:
- [ ] Request with SSN returns 400 with `{"error": "PII detected", "types": ["ssn"]}`
- [ ] Clean request proceeds to next step
- [ ] Multiple PII types all reported

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: (X tests, Y% coverage)
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/2.1-pii-detection
- **Notes**: (any additional context)

---

### Task 2.1 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/2.1-pii-detection`
- [ ] Commit: `git commit -m "feat: PII detection gate"`
- [ ] Delete branch: `git branch -d feature/2.1-pii-detection`

---

## Phase 3: AI Interpretation

**Goal**: Integrate Claude API for lab value interpretation
**Duration**: Day 3-4

### Task 3.1: Claude Integration

**Git**: Create branch `feature/3.1-claude-integration` when starting first subtask.

---

**Subtask 3.1.1: Claude API Integration (Single Session)**

**Prerequisites**:
- [x] 2.1.2: PII Gate Middleware

**Deliverables**:
- [ ] Create `src/labbot/interpreter.py`
- [ ] Implement `interpret_lab_values()` function
- [ ] Use Claude Haiku for cost efficiency
- [ ] Create prompt template for medical interpretation
- [ ] Handle API errors gracefully

**Prompt structure**:
```python
INTERPRETATION_PROMPT = """You are a medical lab results interpreter helping patients understand their results.

For each lab value, provide:
1. A plain-language explanation of what the test measures
2. Whether the value is normal, borderline, or abnormal
3. What this might mean for their health (without diagnosing)
4. A citation to an authoritative source (Mayo Clinic, NIH, etc.)

Lab values to interpret:
{lab_values}

Respond in JSON format matching this structure:
{schema}

Remember: Always recommend consulting a healthcare provider for medical advice.
"""
```

**Success Criteria**:
- [ ] API key loaded from environment
- [ ] Haiku model used (`claude-3-haiku-20240307`)
- [ ] Response parsed into `InterpretationResponse`
- [ ] API errors return 503 with message

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: (X tests, Y% coverage)
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/3.1-claude-integration
- **Notes**: (any additional context)

---

**Subtask 3.1.2: Lab Value Interpreter (Single Session)**

**Prerequisites**:
- [x] 3.1.1: Claude API Integration

**Deliverables**:
- [ ] Complete `/api/interpret` endpoint implementation
- [ ] Connect schema validation → PII check → Claude interpretation
- [ ] Return `InterpretationResponse` with all fields
- [ ] Add integration tests (mock Claude API)

**Success Criteria**:
- [ ] Full pipeline works end-to-end
- [ ] Response includes disclaimer
- [ ] Severity levels correctly assigned
- [ ] Citations included in responses

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: (X tests, Y% coverage)
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/3.1-claude-integration
- **Notes**: (any additional context)

---

**Subtask 3.1.3: Citation Generator (Single Session)**

**Prerequisites**:
- [x] 3.1.2: Lab Value Interpreter

**Deliverables**:
- [ ] Create `src/labbot/citations.py`
- [ ] Map common lab tests to authoritative sources
- [ ] Include URL templates for Mayo Clinic, NIH, MedlinePlus
- [ ] Fallback to generic medical reference

**Success Criteria**:
- [ ] Common tests (CBC, metabolic panel) have specific citations
- [ ] Unknown tests get generic citation
- [ ] URLs are valid and follow patterns

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: (X tests, Y% coverage)
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/3.1-claude-integration
- **Notes**: (any additional context)

---

### Task 3.1 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/3.1-claude-integration`
- [ ] Commit: `git commit -m "feat: Claude API integration for lab interpretation"`
- [ ] Delete branch: `git branch -d feature/3.1-claude-integration`

---

## Phase 4: Web Frontend

**Goal**: Create simple, responsive web UI
**Duration**: Day 4-5

### Task 4.1: Frontend Implementation

**Git**: Create branch `feature/4.1-frontend` when starting first subtask.

---

**Subtask 4.1.1: Static HTML/CSS/JS Frontend (Single Session)**

**Prerequisites**:
- [x] 3.1.3: Citation Generator

**Deliverables**:
- [ ] Create `src/labbot/static/index.html`
- [ ] Create `src/labbot/static/styles.css`
- [ ] Create `src/labbot/static/app.js`
- [ ] Configure FastAPI to serve static files
- [ ] Include sample JSON button

**UI Elements**:
- Header with LabBot title and disclaimer
- JSON textarea input
- "Load Sample" button with example CBC data
- "Interpret" submit button
- Results display area
- Loading spinner

**Success Criteria**:
- [ ] Page loads at root URL
- [ ] Sample data populates textarea
- [ ] Responsive on mobile widths
- [ ] Medical disclaimer prominently displayed

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: Manual UI verification
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/4.1-frontend
- **Notes**: (any additional context)

---

**Subtask 4.1.2: API Integration (Single Session)**

**Prerequisites**:
- [x] 4.1.1: Static HTML/CSS/JS Frontend

**Deliverables**:
- [ ] JavaScript fetch to `/api/interpret`
- [ ] Client-side PII warning (pre-submission check)
- [ ] Error handling and display
- [ ] Loading state management

**Success Criteria**:
- [ ] Submit sends POST to API
- [ ] Client-side PII check warns user
- [ ] Network errors display message
- [ ] Loading spinner shows during request

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: Manual UI verification
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/4.1-frontend
- **Notes**: (any additional context)

---

**Subtask 4.1.3: Results Display (Single Session)**

**Prerequisites**:
- [x] 4.1.2: API Integration

**Deliverables**:
- [ ] Render interpretation results as cards
- [ ] Color-code severity levels (green/yellow/red)
- [ ] Display citations as links
- [ ] Show summary and disclaimer

**Success Criteria**:
- [ ] Each lab value in separate card
- [ ] Severity visually distinct
- [ ] Citations clickable
- [ ] Disclaimer always visible

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: Manual UI verification
- **Build**: ruff: pass, mypy: pass
- **Branch**: feature/4.1-frontend
- **Notes**: (any additional context)

---

### Task 4.1 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/4.1-frontend`
- [ ] Commit: `git commit -m "feat: web frontend with results display"`
- [ ] Delete branch: `git branch -d feature/4.1-frontend`

---

## Phase 5: AWS Deployment

**Goal**: Deploy to AWS Lambda with auto-deploy from GitHub
**Duration**: Day 5-6

### Task 5.1: AWS Deployment

**Git**: Create branch `feature/5.1-aws-deploy` when starting first subtask.

---

**Subtask 5.1.1: SAM Template (Single Session)**

**Prerequisites**:
- [x] 4.1.3: Results Display

**Deliverables**:
- [ ] Create `template.yaml` (SAM template)
- [ ] Configure Lambda function with Mangum handler
- [ ] Configure API Gateway with CORS
- [ ] Add environment variable for ANTHROPIC_API_KEY

**template.yaml structure**:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: LabBot - Lab Results Interpreter

Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Runtime: python3.11

Resources:
  LabBotFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: labbot.main.handler
      Events:
        Api:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
      Environment:
        Variables:
          ANTHROPIC_API_KEY: !Ref AnthropicApiKey

Parameters:
  AnthropicApiKey:
    Type: String
    NoEcho: true

Outputs:
  ApiUrl:
    Value: !Sub "https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com"
```

**Success Criteria**:
- [ ] `sam validate` passes
- [ ] `sam build` completes
- [ ] Handler exports correctly with Mangum

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: sam validate
- **Build**: SAM build success
- **Branch**: feature/5.1-aws-deploy
- **Notes**: (any additional context)

---

**Subtask 5.1.2: GitHub Actions Deployment (Single Session)**

**Prerequisites**:
- [x] 5.1.1: SAM Template

**Deliverables**:
- [ ] Create `.github/workflows/deploy.yml`
- [ ] Configure AWS credentials via secrets
- [ ] Deploy on push to main
- [ ] Output deployed URL

**deploy.yml structure**:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          
      - uses: aws-actions/setup-sam@v2
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - run: sam build
      
      - run: |
          sam deploy --no-confirm-changeset --no-fail-on-empty-changeset \
            --parameter-overrides AnthropicApiKey=${{ secrets.ANTHROPIC_API_KEY }}
```

**Success Criteria**:
- [ ] Workflow syntax valid
- [ ] Required secrets documented in README
- [ ] Deploys automatically on merge to main

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: N/A (workflow config)
- **Build**: YAML valid
- **Branch**: feature/5.1-aws-deploy
- **Notes**: (any additional context)

---

**Subtask 5.1.3: End-to-End Verification (Single Session)**

**Prerequisites**:
- [x] 5.1.2: GitHub Actions Deployment

**Deliverables**:
- [ ] Create `tests/test_e2e.py` for deployed API
- [ ] Test health endpoint
- [ ] Test interpretation with sample data
- [ ] Update README with deployment instructions

**Success Criteria**:
- [ ] Deployed API responds to health check
- [ ] Interpretation returns valid response
- [ ] README has complete setup instructions

---

**Completion Notes**:
- **Implementation**: (describe what was done)
- **Files Created**: (filename - line count)
- **Files Modified**: (filename)
- **Tests**: E2E tests pass against deployed API
- **Build**: Full pipeline verified
- **Branch**: feature/5.1-aws-deploy
- **Notes**: (any additional context)

---

### Task 5.1 Complete - Squash Merge
- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge to main: `git checkout main && git merge --squash feature/5.1-aws-deploy`
- [ ] Commit: `git commit -m "feat: AWS Lambda deployment with GitHub Actions"`
- [ ] Delete branch: `git branch -d feature/5.1-aws-deploy`

---

## Git Workflow

### Branch Strategy
- **ONE branch per TASK** (e.g., `feature/1.1-fastapi-app`)
- **NO branches for individual subtasks** - subtasks are commits within the task branch
- Branch naming: `feature/{phase}.{task}-{description}`

### Commit Strategy
- **One commit per subtask** with semantic message
- Format: `feat(scope): description`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

### Merge Strategy
- **Squash merge when task is complete**
- Delete feature branch after merge

---

## Ready to Build

Each subtask is paint-by-numbers with explicit deliverables and testable success criteria.

**To start implementation**, use this prompt:

```
Please read CLAUDE.md and DEVELOPMENT_PLAN.md completely, then implement subtask [0.1.1], following all rules and marking checkboxes as you complete each item.
```

---

*Generated by DevPlan methodology*
