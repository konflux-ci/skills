# Testing Framework Documentation

## Overview

This repository uses pytest for testing Konflux skills. The test framework validates that skills produce expected outputs when invoked by Claude.

## Architecture

### Key Components

1. **conftest.py** - Pytest configuration and fixtures
   - `pytest_generate_tests()`: Dynamically creates test cases from scenarios.yaml files
   - `worker_home` fixture: Provides isolated temp HOME directories for parallel execution
   - Helper functions: skill discovery, digest computation, expectation checking

2. **test_skills.py** - Main test module
   - Single parameterized test function that handles both generation and validation
   - Uses pytest's native output formatting and reporting

3. **pytest.ini** - Pytest configuration
   - Test discovery patterns
   - Output formatting options
   - Marker definitions

4. **scenarios.yaml** - Test definitions (per skill)
   - Located in `<skill-name>/tests/scenarios.yaml`
   - Defines prompts, expected outputs, and model to use

## Installation

Install dependencies:

```bash
make install
# or
pip install -r requirements.txt
```

Requirements:
- pytest >= 8.0.0
- pytest-xdist >= 3.5.0 (for parallel execution)
- PyYAML >= 6.0

## Usage

### Running Tests

```bash
# Run all tests (with linting and generation)
make

# Run tests only (skip linting and generation)
make test-only

# Run tests for specific skill
make test SKILL=understanding-konflux-resources

# Run with custom number of workers
make test WORKERS=4
```

### Generating Results

```bash
# Generate results for all skills
make generate

# Generate for specific skill
make generate SKILL=understanding-konflux-resources

# Use fewer workers
make generate WORKERS=2
```

### Using pytest directly

```bash
# Run tests
pytest

# Run with parallel execution (8 workers)
pytest -n 8

# Run in generate mode
pytest --generate

# Run specific skill
pytest --skill understanding-konflux-resources

# Verbose output
pytest -v

# Show only failures
pytest -q
```

## How It Works

### Test Discovery

1. pytest calls `pytest_generate_tests()` in conftest.py
2. Function discovers all skills with scenarios.yaml files
3. For each scenario sample, creates a parameterized test case
4. Test IDs follow format: `{skill}::{scenario}[{sample}]`

### Test Execution

Each test case runs `test_skill_scenario()` which:

**In generate mode (`--generate`):**
1. Checks if result file exists with matching digest
2. If up-to-date, skips with "matching digest" message
3. Otherwise, invokes Claude with the prompt
4. Saves output with digest header to result file
5. Marks test as skipped (generation succeeded)

**In test mode (default):**
1. Loads result file from `<skill>/tests/results/`
2. Verifies digest matches current skill content
3. Checks content against expectations from scenarios.yaml
4. Reports failures using pytest's assertion framework

### Parallel Execution

- Uses pytest-xdist for parallel test execution
- Each worker gets isolated temp HOME directory (via `worker_home` fixture)
- Avoids file watcher conflicts that plagued the old implementation
- Worker HOME directories contain:
  - Symlinks to skill directories in `.claude/skills/`
  - Copy of gcloud credentials for Claude authentication

### Digest-Based Skip Logic

- Skill digest computed from all non-test files
- Stored in first line of each result file: `# skill_digest: <hash>`
- During generation:
  - Existing files with matching digest are skipped
  - Only modified skills trigger regeneration
- During testing:
  - Digest mismatch = skill changed, need to regenerate

## Scenario Configuration

Example scenarios.yaml:

```yaml
skill_name: understanding-konflux-resources
description: Tests for Konflux resource understanding

test_scenarios:
  - name: rp-namespace-placement
    description: Test RP abbreviation recognition
    prompt: "Where should I create my RP in Konflux?"
    model: haiku
    samples: 3
    expected:
      recognizes: ReleasePlan
      contains_keywords:
        - tenant namespace
        - ReleasePlan
      does_not_contain:
        - Resource Pool
    baseline_failure: "Agent didn't recognize RP abbreviation"
```

### Expectation Types

- `recognizes`: Single term that must appear (case-insensitive)
- `contains_keywords`: List of terms that must all appear
- `does_not_contain`: List of terms that must NOT appear

## Advantages Over Old Framework

### Removed Custom Code

The pytest refactor eliminates:
- Custom test result formatting (~50 lines) → use pytest's native formatting
- Custom test discovery (~30 lines) → use pytest's parameterization
- Custom parallel execution logic (~40 lines) → use pytest-xdist
- Custom color codes → use pytest's color output
- Custom summary reporting (~50 lines) → use pytest's summary

### Simplified Codebase

**Old framework (test.py):**
- 509 lines of Python
- Custom CLI argument parsing
- Manual parallel execution with multiprocessing.Pool
- Custom result formatting and color codes
- Complex test result aggregation

**New framework (conftest.py + test_skills.py):**
- ~310 lines total (40% reduction)
- pytest's built-in CLI options
- pytest-xdist handles parallelization
- Native pytest output and reporting
- Standard pytest test collection/execution

### Better Output

Pytest provides:
- Clearer test names in output
- Better failure reporting with context
- Progress indicators
- Summary statistics
- Integration with IDE test runners
- Standard test report formats (JUnit XML, etc.)

### Easier to Extend

Adding new features is simpler:
- New expectation types: just update `check_expectations()`
- New fixtures: add to conftest.py
- Custom markers: register in pytest.ini
- Plugins: install via pip and configure

## Migration Notes

The refactored framework is **fully compatible** with existing:
- scenarios.yaml files (no changes needed)
- Result files (same format with digest headers)
- Makefile targets (same commands work)
- Skill directory structure

No test data or results need to be regenerated.

## Troubleshooting

### Tests fail with "EMFILE" error

This should be fixed by pytest-xdist's worker isolation, but if it occurs:
- Reduce number of workers: `make test WORKERS=2`
- Check system file descriptor limits: `ulimit -n`

### Tests skip with "matching digest"

This is expected behavior during generation - the result file is already up-to-date.

### Digest mismatch errors

Skill content changed. Regenerate results:
```bash
make generate SKILL=<skill-name>
```

### Claude invocation fails

- Check Claude CLI is installed: `which claude`
- Verify authentication: `claude --version`
- Check gcloud credentials: `gcloud auth list`
