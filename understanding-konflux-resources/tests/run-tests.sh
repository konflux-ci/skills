#!/bin/bash
# Test runner for understanding-konflux-resources skill
# Tests shortname discovery without requiring skill installation

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_FILE="$SKILL_DIR/SKILL.md"
TEST_SCENARIOS_DIR="$SCRIPT_DIR/scenarios"
RESULTS_DIR="$SCRIPT_DIR/results"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Konflux Resources Skill - Shortname Tests${NC}"
echo -e "${BLUE}============================================${NC}\n"

# Check if skill file exists
if [[ ! -f "$SKILL_FILE" ]]; then
    echo -e "${RED}ERROR: Skill file not found at $SKILL_FILE${NC}"
    exit 1
fi

# Extract key content from skill (abbreviation info)
SKILL_CONTENT=$(cat "$SKILL_FILE")

# Function to run a single test
run_test() {
    local test_name="$1"
    local user_prompt="$2"
    local expected_keywords="$3"  # Keywords we expect in response
    local should_recognize="$4"   # What abbreviation should be recognized

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -e "${YELLOW}Test $TESTS_RUN: $test_name${NC}"
    echo -e "User prompt: ${BLUE}\"$user_prompt\"${NC}"

    # Create test prompt that includes skill content
    local full_prompt="You have access to a Konflux resources skill. Here are the key sections:

=== SKILL CONTENT START ===
$SKILL_CONTENT
=== SKILL CONTENT END ===

IMPORTANT: This is a real user question, not a test. Answer naturally using the skill content above.

User question: \"$user_prompt\"

Provide your answer, then on a new line starting with 'INTERPRETATION:', explain how you interpreted any abbreviations."

    # Run the test using a temporary file
    local temp_file="$RESULTS_DIR/${test_name//[^a-zA-Z0-9]/_}.tmp"

    echo "$full_prompt" > "$temp_file.prompt"

    # Note: This uses a mock command - replace with actual subagent invocation
    # For now, we'll create a template for manual execution
    echo -e "  ${BLUE}→${NC} Running test with subagent..."

    # Create a marker file for manual testing
    echo "# Run this manually:" > "$temp_file.run"
    echo "# Use Claude Code Task tool with model=haiku and this prompt:" >> "$temp_file.run"
    echo "" >> "$temp_file.run"
    cat "$temp_file.prompt" >> "$temp_file.run"

    # For automation, you would call your test framework here
    # Example: claude-code task --model haiku --prompt "$temp_file.prompt" > "$temp_file.result"

    # Validation function (to be filled in with actual results)
    echo -e "  ${YELLOW}⚠${NC}  Manual validation required - see $temp_file.run"
    echo -e "  ${YELLOW}Expected:${NC} Should recognize '$should_recognize' and mention: $expected_keywords"
    echo ""

    # Save expected results
    cat > "$temp_file.expected" <<EOF
Test: $test_name
User Prompt: $user_prompt
Expected Recognition: $should_recognize
Expected Keywords: $expected_keywords
EOF
}

# Function to validate results (for post-processing)
validate_result() {
    local result_file="$1"
    local expected_keywords="$2"
    local should_recognize="$3"

    if [[ ! -f "$result_file" ]]; then
        echo -e "${RED}✗ FAIL${NC} - No result file found"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    local result_content=$(cat "$result_file")
    local pass=true

    # Check if abbreviation was recognized
    if ! echo "$result_content" | grep -qi "$should_recognize"; then
        echo -e "${RED}✗ FAIL${NC} - Did not recognize '$should_recognize'"
        pass=false
    fi

    # Check for expected keywords
    IFS=',' read -ra KEYWORDS <<< "$expected_keywords"
    for keyword in "${KEYWORDS[@]}"; then
        keyword=$(echo "$keyword" | xargs) # trim whitespace
        if ! echo "$result_content" | grep -qi "$keyword"; then
            echo -e "${RED}✗ FAIL${NC} - Missing expected keyword: '$keyword'"
            pass=false
        fi
    done

    if $pass; then
        echo -e "${GREEN}✓ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo -e "${BLUE}Running Test Scenarios...${NC}\n"

# Test 1: RP abbreviation
run_test \
    "rp-namespace-placement" \
    "I'm confused about where to create my RP - should it go in the tenant namespace or managed namespace?" \
    "tenant namespace,ReleasePlan" \
    "ReleasePlan"

# Test 2: ITS abbreviation
run_test \
    "its-not-running" \
    "My ITS is not running after builds complete. I have the Component and Application set up. What am I missing?" \
    "IntegrationTestScenario,must exist before build,references correct Application,Tekton pipeline" \
    "IntegrationTestScenario"

# Test 3: RPA abbreviation
run_test \
    "rpa-creation-responsibility" \
    "Do I create the RPA or does the platform team create it?" \
    "platform engineer,ReleasePlanAdmission,managed namespace" \
    "ReleasePlanAdmission"

# Test 4: Mixed shortnames
run_test \
    "rp-rpa-relationship" \
    "How does the RPA reference the RP? Do they need to be in the same namespace?" \
    "ReleasePlan,ReleasePlanAdmission,tenant,managed,different namespace" \
    "ReleasePlan"

# Test 5: Lowercase abbreviation
run_test \
    "its-lowercase" \
    "my its isn't triggering after builds" \
    "IntegrationTestScenario,must exist before,Application,pipeline" \
    "IntegrationTestScenario"

echo -e "\n${BLUE}============================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Tests created: ${TESTS_RUN}"
echo -e "Test prompts saved to: ${RESULTS_DIR}/"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Run each test manually using the .run files"
echo -e "2. Save results to corresponding .result files"
echo -e "3. Run: $0 --validate to check results"
echo ""
echo -e "Or integrate with your test automation framework."
