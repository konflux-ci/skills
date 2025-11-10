#!/usr/bin/env python3
"""
Test framework for Konflux skills.

This script handles both test generation (invoking Claude) and test validation
(comparing results against expectations).

Usage:
    python test.py generate [--skill SKILL_NAME]  # Generate test results
    python test.py test [--skill SKILL_NAME]      # Run tests
"""

import argparse
import hashlib
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Number of parallel workers for generation
# Set to 1 due to file handle limits when using --plugin-dir
# (Each plugin-dir creates many file watchers)
PARALLEL_WORKERS = 1

# ANSI color codes
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"


def find_skills(base_dir: Path = Path(".")) -> List[Path]:
    """Find all skill directories (those containing SKILL.md)."""
    skills = []
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
            print(f"Warning: Could not hash {file_path}: {e}", file=sys.stderr)

    return hasher.hexdigest()


def load_scenarios(skill_dir: Path) -> Optional[Dict]:
    """Load scenarios.yaml from skill's tests directory."""
    scenarios_file = skill_dir / "tests" / "scenarios.yaml"
    if not scenarios_file.exists():
        return None

    with open(scenarios_file) as f:
        return yaml.safe_load(f)


def invoke_claude(prompt: str, skill_dir: Path, model: str = "haiku") -> str:
    """
    Invoke Claude CLI with the given prompt, requiring skill discovery.

    Uses --plugin-dir to load the skill directory as a plugin.
    The prompt is passed via stdin (required when using --plugin-dir).
    Runs from /tmp to avoid picking up CLAUDE.md from the repository.
    """
    # Get absolute path to parent directory (repository root)
    repo_root = skill_dir.parent.absolute()

    # Invoke Claude with --plugin-dir to load the skill
    cmd = [
        "claude",
        "--print",
        "--model", model,
        "--plugin-dir", str(repo_root)
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,  # Pass prompt via stdin
            capture_output=True,
            text=True,
            check=True,
            cwd="/tmp"  # Run from /tmp to avoid picking up CLAUDE.md from repo
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error invoking Claude: {e}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        raise


def generate_one_sample(
    skill_name: str,
    skill_dir: Path,
    digest: str,
    results_dir: Path,
    scenario_name: str,
    prompt: str,
    model: str,
    sample_num: int,
    total_samples: int
) -> Tuple[bool, str]:
    """
    Generate a single result file for one scenario sample.

    Returns (success, message) tuple.
    """
    result_file = results_dir / f"{scenario_name}.{sample_num}.txt"

    try:
        output = invoke_claude(prompt, skill_dir, model)

        # Write result with digest comment on first line
        with open(result_file, "w") as f:
            f.write(f"# skill_digest: {digest}\n")
            f.write(output)

        return (True, f"{scenario_name} sample {sample_num}/{total_samples}")
    except Exception as e:
        return (False, f"{scenario_name} sample {sample_num}/{total_samples}: {e}")


def generate_results(skill_dir: Path, digest: str) -> bool:
    """Generate test results for a skill using parallel execution."""
    scenarios_data = load_scenarios(skill_dir)
    if not scenarios_data:
        print(f"No scenarios.yaml found in {skill_dir}/tests/")
        return True

    skill_name = skill_dir.name
    print(f"\nGenerating results for skill: {skill_name}")

    # Create results directory
    results_dir = skill_dir / "tests" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Collect all jobs to run (skip files with matching digest)
    jobs = []
    skipped = 0
    scenarios = scenarios_data.get("test_scenarios", [])

    for scenario in scenarios:
        name = scenario["name"]
        prompt = scenario["prompt"]
        model = scenario.get("model", "haiku")
        samples = scenario.get("samples", 1)

        for i in range(1, samples + 1):
            result_file = results_dir / f"{name}.{i}.txt"

            # Check if file exists with matching digest
            if result_file.exists():
                try:
                    with open(result_file) as f:
                        first_line = f.readline()
                    if first_line.startswith("# skill_digest:"):
                        file_digest = first_line.split(":", 1)[1].strip()
                        if file_digest == digest:
                            # File already has correct digest, skip regeneration
                            skipped += 1
                            continue
                except Exception:
                    # If we can't read the file, regenerate it
                    pass

            jobs.append((
                skill_name,
                skill_dir,
                digest,
                results_dir,
                name,
                prompt,
                model,
                i,
                samples
            ))

    total_jobs = len(jobs)

    if skipped > 0:
        print(f"  Skipping {skipped} files with matching digest")

    if total_jobs == 0:
        print(f"  All result files up to date!")
        return True

    print(f"  Running {total_jobs} generation jobs with {PARALLEL_WORKERS} parallel workers...\n")

    # Run jobs in parallel
    with Pool(processes=PARALLEL_WORKERS) as pool:
        results = pool.starmap(generate_one_sample, jobs)

    # Report results
    successes = 0
    failures = 0

    for success, message in results:
        if success:
            print(f"  ✓ {message}")
            successes += 1
        else:
            print(f"  ✗ {message}")
            failures += 1

    print(f"\n  Summary: {successes} succeeded, {failures} failed")

    return failures == 0


def check_expectations(content: str, expected: Dict) -> List[str]:
    """
    Check if content meets expectations.

    Returns list of failure messages (empty if all pass).
    """
    failures = []
    content_lower = content.lower()

    # Check recognizes
    if "recognizes" in expected:
        term = expected["recognizes"]
        if term.lower() not in content_lower:
            failures.append(f"Should recognize '{term}' but doesn't")

    # Check contains_keywords
    if "contains_keywords" in expected:
        for keyword in expected["contains_keywords"]:
            if keyword.lower() not in content_lower:
                failures.append(f"Should contain '{keyword}' but doesn't")

    # Check does_not_contain
    if "does_not_contain" in expected:
        for keyword in expected["does_not_contain"]:
            if keyword.lower() in content_lower:
                failures.append(f"Should NOT contain '{keyword}' but does")

    return failures


def test_results(skill_dir: Path, current_digest: str) -> bool:
    """Test results for a skill."""
    scenarios_data = load_scenarios(skill_dir)
    if not scenarios_data:
        print(f"No scenarios.yaml found in {skill_dir}/tests/")
        return True

    skill_name = skill_dir.name
    print(f"\nTesting skill: {skill_name}")

    results_dir = skill_dir / "tests" / "results"
    if not results_dir.exists():
        print(f"  ERROR: No results directory found. Run 'make generate' first.")
        return False

    all_passed = True
    scenarios = scenarios_data.get("test_scenarios", [])

    # Track statistics for summary
    total_scenarios = len(scenarios)
    passed_scenarios = 0
    total_samples = 0
    passed_samples = 0

    for scenario in scenarios:
        name = scenario["name"]
        samples = scenario.get("samples", 1)
        expected = scenario.get("expected", {})

        # Track if this scenario passes (all samples must pass)
        scenario_passed = True
        scenario_sample_count = 0

        # Print scenario header (will update with prefix after testing)
        scenario_failures = []

        for i in range(1, samples + 1):
            total_samples += 1
            scenario_sample_count += 1
            result_file = results_dir / f"{name}.{i}.txt"

            if not result_file.exists():
                scenario_failures.append(f"    {result_file}: ✗ (file not found)")
                scenario_passed = False
                all_passed = False
                continue

            # Read result file
            with open(result_file) as f:
                lines = f.readlines()

            # Check digest
            if not lines or not lines[0].startswith("# skill_digest:"):
                scenario_failures.append(f"    {result_file}: ✗ (missing digest)")
                scenario_passed = False
                all_passed = False
                continue

            file_digest = lines[0].split(":", 1)[1].strip()
            if file_digest != current_digest:
                scenario_failures.append(f"    {result_file}: ✗ (skill changed, digest mismatch)")
                scenario_failures.append(f"      Expected: {current_digest}")
                scenario_failures.append(f"      Found:    {file_digest}")
                scenario_failures.append(f"      Run 'make generate' to regenerate results.")
                scenario_passed = False
                all_passed = False
                continue

            # Check expectations
            content = "".join(lines[1:])  # Skip digest line
            failures = check_expectations(content, expected)

            if failures:
                scenario_failures.append(f"    {result_file}: ✗")
                for failure in failures:
                    scenario_failures.append(f"      - {failure}")
                scenario_passed = False
                all_passed = False
            else:
                scenario_failures.append(f"    Sample {i}: ✓")
                passed_samples += 1

        # Print scenario with colored prefix
        if scenario_passed:
            print(f"  {COLOR_GREEN}PASS{COLOR_RESET} Scenario: {name}")
            passed_scenarios += 1
        else:
            print(f"  {COLOR_RED}FAIL{COLOR_RESET} Scenario: {name}")

        # Print all sample results
        for line in scenario_failures:
            print(line)

    # Print summary
    print("\n" + "=" * 70)
    print(f"{COLOR_GREEN if all_passed else COLOR_RED}TEST SUMMARY{COLOR_RESET}")
    print("=" * 70)

    failed_scenarios = total_scenarios - passed_scenarios
    failed_samples = total_samples - passed_samples

    print(f"Scenarios: {COLOR_GREEN}{passed_scenarios} passed{COLOR_RESET}, "
          f"{COLOR_RED if failed_scenarios > 0 else COLOR_GREEN}{failed_scenarios} failed{COLOR_RESET}, "
          f"{total_scenarios} total")

    print(f"Samples:   {COLOR_GREEN}{passed_samples} passed{COLOR_RESET}, "
          f"{COLOR_RED if failed_samples > 0 else COLOR_GREEN}{failed_samples} failed{COLOR_RESET}, "
          f"{total_samples} total")

    if all_passed:
        print(f"\n{COLOR_GREEN}✓ All tests passed!{COLOR_RESET}")
    else:
        print(f"\n{COLOR_RED}✗ Some tests failed{COLOR_RESET}")

    print("=" * 70)

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Test framework for Konflux skills")
    parser.add_argument(
        "command",
        choices=["generate", "test"],
        help="Command to run"
    )
    parser.add_argument(
        "--skill",
        help="Specific skill to process (default: all skills)"
    )

    args = parser.parse_args()

    # Find skills to process
    if args.skill:
        skills = [Path(args.skill)]
        if not skills[0].exists():
            print(f"Error: Skill directory '{args.skill}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        skills = find_skills()

    if not skills:
        print("No skills found", file=sys.stderr)
        sys.exit(1)

    # Process each skill
    all_success = True
    for skill_dir in skills:
        digest = compute_skill_digest(skill_dir)

        if args.command == "generate":
            success = generate_results(skill_dir, digest)
        else:  # test
            success = test_results(skill_dir, digest)

        if not success:
            all_success = False

    # Exit with appropriate code
    if all_success:
        print("\n✓ All tests passed" if args.command == "test" else "\n✓ Generation complete")
        sys.exit(0)
    else:
        print(f"\n✗ {'Tests failed' if args.command == 'test' else 'Generation failed'}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
