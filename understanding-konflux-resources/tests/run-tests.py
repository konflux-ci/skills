#!/usr/bin/env python3
"""
Test runner for understanding-konflux-resources skill
Tests shortname discovery by providing skill content to test subagents
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

# Test configuration
TESTS = [
    {
        "name": "rp-namespace-placement",
        "prompt": "I'm confused about where to create my RP - should it go in the tenant namespace or managed namespace?",
        "expected_recognition": "ReleasePlan",
        "expected_keywords": ["tenant", "ReleasePlan", "RP"],
        "should_not_contain": ["Resource Pool"],  # Should not confuse with non-Konflux terms
    },
    {
        "name": "its-not-running",
        "prompt": "My ITS is not running after builds complete. I have the Component and Application set up. What am I missing?",
        "expected_recognition": "IntegrationTestScenario",
        "expected_keywords": ["IntegrationTestScenario", "before build", "Application", "pipeline"],
        "should_not_contain": [],
    },
    {
        "name": "rpa-creation-responsibility",
        "prompt": "Do I create the RPA or does the platform team create it?",
        "expected_recognition": "ReleasePlanAdmission",
        "expected_keywords": ["platform engineer", "ReleasePlanAdmission", "managed namespace"],
        "should_not_contain": ["you create", "user creates"],
    },
    {
        "name": "rp-rpa-relationship",
        "prompt": "How does the RPA reference the RP? Do they need to be in the same namespace?",
        "expected_recognition": "ReleasePlan",
        "expected_keywords": ["ReleasePlan", "ReleasePlanAdmission", "tenant", "managed"],
        "should_not_contain": ["same namespace"],
    },
    {
        "name": "its-lowercase",
        "prompt": "my its isn't triggering after builds",
        "expected_recognition": "IntegrationTestScenario",
        "expected_keywords": ["IntegrationTestScenario", "ITS"],
        "should_not_contain": [],
    },
]


def get_skill_content() -> str:
    """Read the skill file content"""
    script_dir = Path(__file__).parent
    skill_file = script_dir.parent / "SKILL.md"

    if not skill_file.exists():
        print(f"{Colors.RED}ERROR: Skill file not found at {skill_file}{Colors.NC}")
        sys.exit(1)

    return skill_file.read_text()


def create_test_prompt(skill_content: str, user_question: str) -> str:
    """Create a test prompt that includes skill content"""
    return f"""You have access to a Konflux resources skill. Here are the key sections:

=== SKILL CONTENT START ===
{skill_content}
=== SKILL CONTENT END ===

IMPORTANT: This is a real user question, not a test. Answer naturally using the skill content above.

User question: "{user_question}"

After providing your answer, add a section starting with "INTERPRETATION:" explaining:
1. How you interpreted any abbreviations (e.g., RP, ITS, RPA)
2. Which parts of the skill you used
3. Your confidence level
"""


def run_test_with_claude(prompt: str, test_name: str, results_dir: Path) -> str:
    """
    Run a test using Claude Code's task functionality

    This is a placeholder - you'll need to integrate with your actual
    Claude Code task runner or use the API directly
    """
    # Save prompt for manual execution
    prompt_file = results_dir / f"{test_name}.prompt.txt"
    prompt_file.write_text(prompt)

    # For actual automation, you would:
    # 1. Use Claude Code's Python API if available
    # 2. Use subprocess to call claude-code CLI
    # 3. Use Anthropic API directly

    print(f"  {Colors.BLUE}→{Colors.NC} Prompt saved to: {prompt_file}")
    print(f"  {Colors.YELLOW}⚠{Colors.NC}  Manual execution required")

    # Return empty string since we're not actually running it
    return ""


def validate_result(result: str, test_config: Dict) -> Tuple[bool, List[str]]:
    """Validate test result against expected criteria"""
    errors = []
    result_lower = result.lower()

    # Check for expected recognition
    if test_config["expected_recognition"].lower() not in result_lower:
        errors.append(f"Did not recognize '{test_config['expected_recognition']}'")

    # Check for expected keywords
    for keyword in test_config["expected_keywords"]:
        if keyword.lower() not in result_lower:
            errors.append(f"Missing expected keyword: '{keyword}'")

    # Check for things that should NOT be present
    for bad_keyword in test_config.get("should_not_contain", []):
        if bad_keyword.lower() in result_lower:
            errors.append(f"Should not contain: '{bad_keyword}'")

    return len(errors) == 0, errors


def main():
    print(f"{Colors.BLUE}{Colors.BOLD}============================================{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}Konflux Resources Skill - Shortname Tests{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}============================================{Colors.NC}\n")

    # Setup
    script_dir = Path(__file__).parent
    results_dir = script_dir / "results"
    results_dir.mkdir(exist_ok=True)

    # Load skill content
    print(f"{Colors.BLUE}Loading skill content...{Colors.NC}")
    skill_content = get_skill_content()
    print(f"{Colors.GREEN}✓{Colors.NC} Skill loaded\n")

    # Run tests
    print(f"{Colors.BLUE}Running Test Scenarios...{Colors.NC}\n")

    tests_run = 0
    tests_passed = 0
    tests_failed = 0

    for test in TESTS:
        tests_run += 1
        test_name = test["name"]

        print(f"{Colors.YELLOW}Test {tests_run}: {test_name}{Colors.NC}")
        print(f"  User prompt: \"{test['prompt']}\"")

        # Create test prompt
        prompt = create_test_prompt(skill_content, test["prompt"])

        # Save prompt
        prompt_file = results_dir / f"{test_name}.prompt.txt"
        prompt_file.write_text(prompt)
        print(f"  {Colors.GREEN}✓{Colors.NC} Prompt saved to: {prompt_file}")

        # Check if result exists
        result_file = results_dir / f"{test_name}.result.txt"
        if result_file.exists():
            result = result_file.read_text()
            passed, errors = validate_result(result, test)

            if passed:
                print(f"  {Colors.GREEN}✓ PASS{Colors.NC}")
                tests_passed += 1
            else:
                print(f"  {Colors.RED}✗ FAIL{Colors.NC}")
                for error in errors:
                    print(f"    - {error}")
                tests_failed += 1
        else:
            print(f"  {Colors.YELLOW}⚠ PENDING{Colors.NC} - Run manually and save to: {result_file}")

        print()

    # Summary
    print(f"{Colors.BLUE}{Colors.BOLD}============================================{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}Test Summary{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}============================================{Colors.NC}")
    print(f"Tests run:    {tests_run}")
    print(f"{Colors.GREEN}Tests passed: {tests_passed}{Colors.NC}")
    if tests_failed > 0:
        print(f"{Colors.RED}Tests failed: {tests_failed}{Colors.NC}")
    print(f"{Colors.YELLOW}Tests pending: {tests_run - tests_passed - tests_failed}{Colors.NC}")
    print()

    # Instructions
    if tests_passed + tests_failed < tests_run:
        print(f"{Colors.YELLOW}Next Steps:{Colors.NC}")
        print(f"1. For each .prompt.txt file in {results_dir}/")
        print(f"2. Run the prompt through Claude Code Task tool (model: haiku)")
        print(f"3. Save the response to corresponding .result.txt file")
        print(f"4. Re-run this script to validate results")
        print()

    # Exit code
    sys.exit(0 if tests_failed == 0 else 1)


if __name__ == "__main__":
    main()
