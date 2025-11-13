"""
Pytest configuration and fixtures for Konflux skills testing.

This module provides fixtures for:
- Discovering skills
- Computing skill digests
- Managing worker home directories for parallel execution
- Loading test scenarios
"""

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import pytest
import yaml


# Number of parallel workers (for pytest-xdist)
# Each worker gets isolated temp HOME to avoid file watcher conflicts
PARALLEL_WORKERS = 8


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--skill",
        action="store",
        default=None,
        help="Run tests for a specific skill only"
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "generate: mark test to generate results (invoke Claude)"
    )
    config.addinivalue_line(
        "markers",
        "test: mark test to validate existing results"
    )


def find_skills(base_dir: Path = Path("skills")) -> List[Path]:
    """Find all skill directories (those containing SKILL.md)."""
    skills = []
    # If base_dir doesn't exist, return empty list
    if not base_dir.exists():
        return skills
    for path in base_dir.iterdir():
        if path.is_dir() and (path / "SKILL.md").exists():
            skills.append(path)
    return sorted(skills)


def compute_skill_digest(skill_dir: Path) -> str:
    """
    Compute SHA256 digest of all non-test files in skill directory.

    Hashes all files except those in tests/ subdirectory, sorted by path
    for consistency.
    """
    hasher = hashlib.sha256()

    # Get all files except those in tests/ directory
    files_to_hash = []
    for root, dirs, files in os.walk(skill_dir):
        # Skip tests directory
        if "tests" in Path(root).parts:
            continue

        for file in sorted(files):
            file_path = Path(root) / file
            files_to_hash.append(file_path)

    # Sort for consistent ordering
    files_to_hash.sort()

    # Hash each file's content
    for file_path in files_to_hash:
        try:
            with open(file_path, "rb") as f:
                hasher.update(file_path.relative_to(skill_dir).as_posix().encode())
                hasher.update(b"\x00")
                hasher.update(f.read())
                hasher.update(b"\x00")
        except Exception as e:
            print(f"Warning: Could not hash {file_path}: {e}")

    return hasher.hexdigest()


def load_scenarios(skill_dir: Path) -> Optional[Dict]:
    """Load scenarios.yaml from skill's tests directory."""
    scenarios_file = skill_dir / "tests" / "scenarios.yaml"
    if not scenarios_file.exists():
        return None

    with open(scenarios_file) as f:
        return yaml.safe_load(f)


def parse_skill_frontmatter(skill_dir: Path) -> Optional[Dict]:
    """
    Parse YAML frontmatter from SKILL.md.

    Returns dict with frontmatter fields, or None if not found.
    """
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return None

    with open(skill_file) as f:
        content = f.read()

    # Check for YAML frontmatter (--- at start and end)
    if not content.startswith("---\n"):
        return None

    # Find the closing ---
    end_marker = content.find("\n---\n", 4)
    if end_marker == -1:
        return None

    # Extract and parse frontmatter
    frontmatter_text = content[4:end_marker]
    try:
        return yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return None


@pytest.fixture(scope="session")
def worker_home(tmp_path_factory, request):
    """
    Create a persistent temp HOME directory for this worker.

    In parallel execution (pytest-xdist), each worker gets its own isolated
    temp HOME to avoid file watcher conflicts. The HOME is reused across
    all tests in this worker for efficiency.
    """
    # Check if we're running with pytest-xdist
    worker_id = getattr(request.config, "workerinput", {}).get("workerid", "master")

    if worker_id == "master":
        # Not using xdist, create a simple temp dir
        temp_dir = tmp_path_factory.mktemp("worker_home")
    else:
        # Using xdist, create worker-specific temp dir
        temp_dir = tmp_path_factory.mktemp(f"worker_{worker_id}")

    return temp_dir


@pytest.fixture(scope="session")
def skills_list(request):
    """Get list of skills to test (all or specific one from --skill option)."""
    skill_name = request.config.getoption("--skill")

    if skill_name:
        # Handle both "skill-name" and "skills/skill-name" formats
        skill_path = Path(skill_name)
        if not skill_path.exists():
            # Try prepending "skills/" if not found
            skill_path = Path("skills") / skill_name
            if not skill_path.exists():
                pytest.fail(f"Skill directory '{skill_name}' not found")
        return [skill_path]
    else:
        return find_skills()


def pytest_generate_tests(metafunc):
    """
    Dynamically generate test cases from scenarios.yaml files.

    This is the core of pytest parameterization - it discovers all scenarios
    across all skills and creates individual test items for each sample.

    Creates both 'generate' and 'test' variants of each test case.
    """
    if "skill_scenario" not in metafunc.fixturenames:
        return

    # Get skill filter if provided
    skill_filter = metafunc.config.getoption("--skill")

    # Discover all skills
    if skill_filter:
        # Handle both "skill-name" and "skills/skill-name" formats
        skill_path = Path(skill_filter)
        if not skill_path.exists():
            skill_path = Path("skills") / skill_filter
        skills = [skill_path]
    else:
        skills = find_skills()

    # Collect all test cases
    test_cases = []
    test_ids = []

    for skill_dir in skills:
        scenarios_data = load_scenarios(skill_dir)
        if not scenarios_data:
            continue

        skill_name = skill_dir.name
        digest = compute_skill_digest(skill_dir)

        for scenario in scenarios_data.get("test_scenarios", []):
            scenario_name = scenario["name"]
            prompt = scenario["prompt"]
            model = scenario.get("model", "haiku")
            samples = scenario.get("samples", 1)
            expected = scenario.get("expected", {})

            for sample_num in range(1, samples + 1):
                test_cases.append({
                    "skill_dir": skill_dir,
                    "skill_name": skill_name,
                    "digest": digest,
                    "scenario_name": scenario_name,
                    "prompt": prompt,
                    "model": model,
                    "sample_num": sample_num,
                    "total_samples": samples,
                    "expected": expected,
                })

                test_ids.append(f"{skill_name}::{scenario_name}[{sample_num}]")

    metafunc.parametrize("skill_scenario", test_cases, ids=test_ids)


def invoke_claude(
    prompt: str,
    skill_dir: Path,
    model: str,
    worker_home: Path,
    scenario_name: str,
    sample_num: int
) -> str:
    """
    Invoke Claude CLI with the given prompt.

    Uses a dedicated temp HOME directory per worker to isolate file watchers.
    The worker_home is reused across all tests in the same worker.

    Args:
        prompt: The prompt to send to Claude
        skill_dir: Path to the skill directory being tested
        model: Model to use (default: haiku)
        worker_home: Path to worker's persistent temp HOME
        scenario_name: Name of the test scenario
        sample_num: Sample number for this test
    """
    # Setup worker home if needed
    skills_dir = worker_home / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    # Symlink the skill (if not already linked)
    skill_link = skills_dir / skill_dir.name
    if not skill_link.exists():
        skill_link.symlink_to(skill_dir.absolute())

    # Always copy gcloud credentials (required for Claude Code API authentication)
    gcloud_source = Path.home() / ".config" / "gcloud"
    gcloud_dest = worker_home / ".config" / "gcloud"
    if gcloud_source.exists() and not gcloud_dest.exists():
        gcloud_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(gcloud_source, gcloud_dest)

    # Copy additional paths specified in scenarios.yaml copy_to_home field
    # (for skill-specific credentials like gh, kubectl configs, etc.)
    scenarios_data = load_scenarios(skill_dir)
    if scenarios_data and "copy_to_home" in scenarios_data:
        for path_str in scenarios_data["copy_to_home"]:
            source_path = Path.home() / path_str
            dest_path = worker_home / path_str

            # Only copy if source exists and dest doesn't (once per worker)
            if source_path.exists() and not dest_path.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)

    # Parse skill frontmatter to get allowed-tools
    frontmatter = parse_skill_frontmatter(skill_dir)
    allowed_tools = ["Skill"]  # Always include Skill tool for skill invocation

    if frontmatter and "allowed-tools" in frontmatter:
        # Parse allowed-tools field (can be string or list)
        tools_value = frontmatter["allowed-tools"]
        if isinstance(tools_value, str):
            # Split by comma and strip whitespace
            tools = [t.strip() for t in tools_value.split(",")]
            allowed_tools.extend(tools)
        elif isinstance(tools_value, list):
            allowed_tools.extend(tools_value)

    # Build --allowed-tools parameter
    allowed_tools_str = ",".join(allowed_tools)

    # Invoke Claude with custom HOME
    cmd = [
        "claude",
        "--print",
        "--debug",
        "--model", model,
        f"--allowed-tools={allowed_tools_str}",
        prompt
    ]

    env = os.environ.copy()
    env["HOME"] = str(worker_home)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            close_fds=True,
            env=env,
            cwd=str(worker_home)  # Run from worker home to avoid project CLAUDE.md
        )
    except subprocess.CalledProcessError as e:
        # Log the error for debugging
        print(f"\n=== Claude command failed ===")
        print(f"Command: {' '.join(cmd)}")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        print(f"===========================\n")
        raise

    # Save debug output (stderr) if present
    if result.stderr:
        debug_log = skill_dir / "tests" / "results" / "debug.log"
        debug_log.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_log, "a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Debug output for: {prompt[:100]}...\n")
            f.write(f"{'='*80}\n")
            f.write(result.stderr)
            f.write("\n")

    # Copy Claude debug log if available
    debug_dir = worker_home / ".claude" / "debug"
    if debug_dir.exists():
        latest_link = debug_dir / "latest"
        if latest_link.exists() and latest_link.is_symlink():
            # Copy debug log to results directory with matching name
            debug_dest = skill_dir / "tests" / "results" / f"{scenario_name}-{sample_num}.debug.txt"
            debug_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(latest_link, debug_dest)

    return result.stdout


def check_expectations(content: str, expected: Dict) -> List[str]:
    """
    Check if content meets expectations.

    Returns list of failure messages (empty if all pass).

    Supports flexible keyword matching:
    - contains_keywords: ["foo", "bar"] - both must be present (AND)
    - contains_keywords: [["foo", "bar"]] - at least one must be present (OR)
    - contains_keywords: ["foo", ["bar", "baz"]] - "foo" must be present AND (bar OR baz)
    """
    failures = []
    content_lower = content.lower()

    # Check contains_keywords
    if "contains_keywords" in expected:
        for keyword in expected["contains_keywords"]:
            # If keyword is a list, at least one phrase must match (OR logic)
            if isinstance(keyword, list):
                if not any(phrase.lower() in content_lower for phrase in keyword):
                    phrase_list = "', '".join(keyword)
                    failures.append(f"Should contain at least one of ['{phrase_list}'] but doesn't")
            # If keyword is a string, it must match (AND logic)
            else:
                if keyword.lower() not in content_lower:
                    failures.append(f"Should contain '{keyword}' but doesn't")

    # Check does_not_contain
    if "does_not_contain" in expected:
        for keyword in expected["does_not_contain"]:
            if keyword.lower() in content_lower:
                failures.append(f"Should NOT contain '{keyword}' but does")

    return failures
