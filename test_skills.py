"""
Test suite for Konflux skills.

This module uses pytest's parameterization to dynamically create tests
from scenarios.yaml files. Each test scenario sample becomes a separate
pytest test case.

Tests can run in two modes:
1. Test mode (default): Validate existing results against expectations
2. Generate mode (--generate): Invoke Claude to create new results
"""

from pathlib import Path

import pytest

from conftest import check_expectations, invoke_claude


def test_skill_scenario(skill_scenario, worker_home, request):
    """
    Test a single skill scenario sample.

    This test is parameterized by pytest_generate_tests() in conftest.py,
    creating one test case per scenario sample across all skills.

    Args:
        skill_scenario: Dict containing scenario parameters
        worker_home: Persistent temp HOME for this worker
        request: Pytest request object for accessing config
    """
    skill_dir = skill_scenario["skill_dir"]
    skill_name = skill_scenario["skill_name"]
    digest = skill_scenario["digest"]
    scenario_name = skill_scenario["scenario_name"]
    prompt = skill_scenario["prompt"]
    model = skill_scenario["model"]
    sample_num = skill_scenario["sample_num"]
    expected = skill_scenario["expected"]

    results_dir = skill_dir / "tests" / "results"
    result_file = results_dir / f"{scenario_name}.{sample_num}.txt"

    # Check if we're in generate mode
    generate_mode = request.config.getoption("--generate")

    if generate_mode:
        # GENERATE MODE: Invoke Claude to create/update result file
        results_dir.mkdir(parents=True, exist_ok=True)

        # Check if we can skip generation (file exists with matching digest)
        skip_generation = False
        if result_file.exists():
            try:
                with open(result_file) as f:
                    first_line = f.readline()
                if first_line.startswith("# skill_digest:"):
                    file_digest = first_line.split(":", 1)[1].strip()
                    if file_digest == digest:
                        skip_generation = True
                        pytest.skip("Result file already up-to-date (matching digest)")
            except Exception:
                pass

        if not skip_generation:
            # Generate new result
            try:
                output = invoke_claude(prompt, skill_dir, model, worker_home)

                # Write result with digest comment
                with open(result_file, "w") as f:
                    f.write(f"# skill_digest: {digest}\n")
                    f.write(output)

                # Mark test as passed (generation succeeded)
                pytest.skip("Result generated successfully")

            except Exception as e:
                pytest.fail(f"Failed to generate result: {e}")

    else:
        # TEST MODE: Validate existing result file
        if not result_file.exists():
            pytest.fail(f"Result file not found: {result_file}\nRun with --generate to create it")

        # Read result file
        with open(result_file) as f:
            lines = f.readlines()

        # Check digest
        if not lines or not lines[0].startswith("# skill_digest:"):
            pytest.fail("Result file missing digest header")

        file_digest = lines[0].split(":", 1)[1].strip()
        if file_digest != digest:
            pytest.fail(
                f"Skill content changed - digest mismatch\n"
                f"Expected: {digest}\n"
                f"Found:    {file_digest}\n"
                f"Run with --generate to regenerate results"
            )

        # Check expectations
        content = "".join(lines[1:])  # Skip digest line
        failures = check_expectations(content, expected)

        if failures:
            failure_msg = "\n".join(f"  - {f}" for f in failures)
            pytest.fail(f"Expectation failures:\n{failure_msg}")
