"""
Test suite for Konflux skills.

This module uses pytest's parameterization to dynamically create tests
from scenarios.yaml files. Each test scenario sample becomes a separate
pytest test case.

Tests are marked with either @pytest.mark.generate or @pytest.mark.test:
- generate: Invoke Claude to create/update result files
- test: Validate existing results against expectations

Use pytest's -m flag to select which mode to run:
  pytest -m generate  # Generate results
  pytest -m test      # Validate results
"""

from pathlib import Path

import pytest

from conftest import check_expectations, invoke_claude


@pytest.mark.generate
def test_generate_result(skill_scenario, worker_home):
    """
    Generate test results by invoking Claude.

    Skips if result file already exists with matching digest.
    """
    skill_dir = skill_scenario["skill_dir"]
    digest = skill_scenario["digest"]
    scenario_name = skill_scenario["scenario_name"]
    prompt = skill_scenario["prompt"]
    model = skill_scenario["model"]
    sample_num = skill_scenario["sample_num"]

    results_dir = skill_dir / "tests" / "results"
    result_file = results_dir / f"{scenario_name}.{sample_num}.txt"

    # Check if we can skip generation (file exists with matching digest)
    should_skip = False
    if result_file.exists():
        try:
            with open(result_file) as f:
                first_line = f.readline()
            if first_line.startswith("# skill_digest:"):
                file_digest = first_line.split(":", 1)[1].strip()
                if file_digest == digest:
                    should_skip = True
        except Exception:
            pass  # If we can't read it, we'll regenerate the result

    # Skip OUTSIDE the try/except so it's not suppressed
    if should_skip:
        pytest.skip("already up-to-date")

    # Generate new result
    results_dir.mkdir(parents=True, exist_ok=True)

    try:
        output = invoke_claude(prompt, skill_dir, model, worker_home)

        # Write result with digest comment
        with open(result_file, "w") as f:
            f.write(f"# skill_digest: {digest}\n")
            f.write(output)

    except Exception as e:
        pytest.fail(f"Failed to generate result: {e}")


@pytest.mark.test
def test_validate_result(skill_scenario):
    """
    Validate existing result file against expectations.

    Checks digest matches and content meets expected criteria.
    """
    skill_dir = skill_scenario["skill_dir"]
    digest = skill_scenario["digest"]
    scenario_name = skill_scenario["scenario_name"]
    sample_num = skill_scenario["sample_num"]
    expected = skill_scenario["expected"]

    result_file = skill_dir / "tests" / "results" / f"{scenario_name}.{sample_num}.txt"

    # Check file exists
    if not result_file.exists():
        pytest.fail(
            f"Result file not found: {result_file}\n"
            "Run 'make generate' to create it"
        )

    # Read result file
    with open(result_file) as f:
        lines = f.readlines()

    # Check digest header
    if not lines or not lines[0].startswith("# skill_digest:"):
        pytest.fail("Result file missing digest header")

    file_digest = lines[0].split(":", 1)[1].strip()
    if file_digest != digest:
        pytest.fail(
            f"Skill content changed - digest mismatch\n"
            f"Expected: {digest}\n"
            f"Found:    {file_digest}\n"
            "Run 'make generate' to regenerate results"
        )

    # Check expectations
    content = "".join(lines[1:])  # Skip digest line
    failures = check_expectations(content, expected)

    if failures:
        failure_msg = "\n".join(f"  - {f}" for f in failures)
        pytest.fail(f"Expectation failures:\n{failure_msg}")
