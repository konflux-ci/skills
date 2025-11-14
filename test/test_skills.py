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

import json
from pathlib import Path

import pytest
import yaml

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
        output = invoke_claude(prompt, skill_dir, model, worker_home, scenario_name, sample_num)

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
        pytest.fail(f"Result file missing digest header\nFile: {result_file}")

    file_digest = lines[0].split(":", 1)[1].strip()
    if file_digest != digest:
        pytest.fail(
            f"Skill content changed - digest mismatch\n"
            f"File: {result_file}\n"
            f"Expected: {digest}\n"
            f"Found:    {file_digest}\n"
            "Run 'make generate' to regenerate results"
        )

    # Check expectations
    content = "".join(lines[1:])  # Skip digest line
    failures = check_expectations(content, expected)

    if failures:
        failure_msg = "\n".join(f"  - {f}" for f in failures)
        pytest.fail(f"Expectation failures:\nFile: {result_file}\n{failure_msg}")


@pytest.mark.test
def test_test_only_skills_not_in_marketplace():
    """
    Validate that test-only skills are not in marketplace.json.

    Test-only skills (like self-test-skill-invocation) are used to verify
    the test framework itself and should never be published.
    """
    # List of skills that should NOT be in marketplace.json
    test_only_skills = {
        "self-test-skill-invocation",
    }

    marketplace_file = Path(".claude-plugin/marketplace.json")
    if not marketplace_file.exists():
        pytest.fail(f"Marketplace file not found: {marketplace_file}")

    with open(marketplace_file) as f:
        marketplace_data = json.load(f)

    # Extract skill names from marketplace
    marketplace_skills = {
        plugin["name"]
        for plugin in marketplace_data.get("plugins", [])
    }

    # Check for test-only skills in marketplace
    forbidden_skills = test_only_skills & marketplace_skills

    if forbidden_skills:
        pytest.fail(
            f"Test-only skills found in marketplace.json: {forbidden_skills}\n"
            "These skills are for testing the framework and should not be published."
        )


@pytest.mark.test
def test_all_skills_in_marketplace():
    """
    Validate that all production skills are listed in marketplace.json.

    This ensures that every skill directory with a SKILL.md file (except
    test-only skills) is properly registered in the marketplace manifest.
    """
    # List of skills that should NOT be in marketplace.json
    test_only_skills = {
        "self-test-skill-invocation",
    }

    # Find all skill directories with SKILL.md files
    skill_dirs = []
    for path in Path(".").iterdir():
        if path.is_dir() and (path / "SKILL.md").exists():
            skill_dirs.append(path)

    # Extract skill names from SKILL.md frontmatter
    skill_names = set()
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        with open(skill_file) as f:
            # Read YAML frontmatter
            content = f.read()
            if content.startswith("---"):
                # Extract frontmatter
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1])
                    skill_name = frontmatter.get("name")
                    if skill_name:
                        skill_names.add(skill_name)

    # Exclude test-only skills
    production_skills = skill_names - test_only_skills

    # Load marketplace.json
    marketplace_file = Path(".claude-plugin/marketplace.json")
    if not marketplace_file.exists():
        pytest.fail(f"Marketplace file not found: {marketplace_file}")

    with open(marketplace_file) as f:
        marketplace_data = json.load(f)

    # Extract skill names from marketplace
    marketplace_skills = {
        plugin["name"]
        for plugin in marketplace_data.get("plugins", [])
    }

    # Find skills missing from marketplace
    missing_skills = production_skills - marketplace_skills

    if missing_skills:
        pytest.fail(
            f"Skills found but not in marketplace.json: {missing_skills}\n"
            "All production skills must be registered in .claude-plugin/marketplace.json"
        )


@pytest.mark.test
def test_all_skills_in_readme():
    """
    Validate that all production skills appear in README.md exactly once.

    This ensures that every skill in marketplace.json (except test-only skills)
    is documented in the README with a dedicated section.
    """
    # List of skills that should NOT be in README
    test_only_skills = {
        "self-test-skill-invocation",
    }

    # Load marketplace.json
    marketplace_file = Path(".claude-plugin/marketplace.json")
    if not marketplace_file.exists():
        pytest.fail(f"Marketplace file not found: {marketplace_file}")

    with open(marketplace_file) as f:
        marketplace_data = json.load(f)

    # Extract skill names from marketplace
    production_skills = {
        plugin["name"]
        for plugin in marketplace_data.get("plugins", [])
    } - test_only_skills

    # Read README.md
    readme_file = Path("README.md")
    if not readme_file.exists():
        pytest.fail(f"README.md not found: {readme_file}")

    with open(readme_file) as f:
        readme_content = f.read()

    # Check each skill appears exactly once
    errors = []
    for skill_name in production_skills:
        count = readme_content.count(skill_name)
        if count == 0:
            errors.append(f"  - '{skill_name}' missing from README.md")
        elif count > 1:
            errors.append(f"  - '{skill_name}' appears {count} times (expected exactly 1)")

    if errors:
        pytest.fail(
            "README.md skill documentation issues:\n" + "\n".join(errors) + "\n\n"
            "Each production skill must appear exactly once in README.md"
        )


@pytest.mark.test
def test_scenarios_yaml_schema():
    """
    Validate all scenarios.yaml files against JSON schema.

    This ensures that all test scenario files follow the expected structure
    and contain all required fields with correct types.
    """
    import jsonschema

    # Load the schema
    schema_file = Path("test/scenarios-schema.json")
    if not schema_file.exists():
        pytest.fail(f"Schema file not found: {schema_file}")

    with open(schema_file) as f:
        schema = json.load(f)

    # Find all scenarios.yaml files
    scenarios_files = list(Path("skills").rglob("scenarios.yaml"))

    if not scenarios_files:
        pytest.fail("No scenarios.yaml files found in skills/ directory")

    errors = []
    for scenarios_file in scenarios_files:
        with open(scenarios_file) as f:
            try:
                scenarios_data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"{scenarios_file}: Invalid YAML - {e}")
                continue

        # Validate against schema
        try:
            jsonschema.validate(instance=scenarios_data, schema=schema)
        except jsonschema.ValidationError as e:
            # Build a helpful error message with the path to the error
            path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            errors.append(f"{scenarios_file} at '{path}': {e.message}")
        except jsonschema.SchemaError as e:
            pytest.fail(f"Invalid schema file: {e.message}")

    if errors:
        error_msg = "\n".join(f"  - {e}" for e in errors)
        pytest.fail(
            f"scenarios.yaml validation errors:\n{error_msg}\n\n"
            "All scenarios.yaml files must conform to test/scenarios-schema.json"
        )
