#!/bin/bash
# Interactive test runner for understanding-konflux-resources skill
# Provides skill content inline to each test without requiring installation

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_FILE="$SKILL_DIR/SKILL.md"

# Check skill file exists
if [[ ! -f "$SKILL_FILE" ]]; then
    echo -e "${RED}ERROR: Skill file not found at $SKILL_FILE${NC}"
    exit 1
fi

# Read skill content
SKILL_CONTENT=$(cat "$SKILL_FILE")

echo -e "${BLUE}${BOLD}============================================${NC}"
echo -e "${BLUE}${BOLD}Interactive Skill Test Runner${NC}"
echo -e "${BLUE}${BOLD}============================================${NC}\n"

echo -e "${YELLOW}This script will show you test prompts.${NC}"
echo -e "${YELLOW}Copy each prompt and run it through Claude Code's Task tool.${NC}\n"

# Test 1
echo -e "${GREEN}${BOLD}Test 1: RP Abbreviation${NC}"
echo -e "${BLUE}Expected: Should recognize RP=ReleasePlan, answer 'tenant namespace'${NC}\n"

cat > /tmp/konflux-test-1.txt <<'EOF'
You have access to a Konflux resources skill. Use it to answer this question.

=== SKILL CONTENT START ===
EOF

cat "$SKILL_FILE" >> /tmp/konflux-test-1.txt

cat >> /tmp/konflux-test-1.txt <<'EOF'
=== SKILL CONTENT END ===

IMPORTANT: This is a real user question, not a test.

User question: "I'm confused about where to create my RP - should it go in the tenant namespace or managed namespace?"

After your answer, add:

INTERPRETATION:
- What does "RP" mean?
- What parts of the skill did you use?
- Confidence level?
EOF

echo -e "${YELLOW}Test prompt saved to: /tmp/konflux-test-1.txt${NC}"
echo -e "${YELLOW}Copy and run this with Claude Code Task tool (model: haiku)${NC}\n"

read -p "Press Enter when you've run Test 1 and are ready for Test 2..."

# Test 2
echo -e "\n${GREEN}${BOLD}Test 2: ITS Abbreviation${NC}"
echo -e "${BLUE}Expected: Should recognize ITS=IntegrationTestScenario, provide troubleshooting${NC}\n"

cat > /tmp/konflux-test-2.txt <<'EOF'
You have access to a Konflux resources skill. Use it to answer this question.

=== SKILL CONTENT START ===
EOF

cat "$SKILL_FILE" >> /tmp/konflux-test-2.txt

cat >> /tmp/konflux-test-2.txt <<'EOF'
=== SKILL CONTENT END ===

IMPORTANT: This is a real user question, not a test.

User question: "My ITS is not running after builds complete. I have the Component and Application set up. What am I missing?"

After your answer, add:

INTERPRETATION:
- What does "ITS" mean?
- What troubleshooting steps did you provide?
- Confidence level?
EOF

echo -e "${YELLOW}Test prompt saved to: /tmp/konflux-test-2.txt${NC}"
echo -e "${YELLOW}Copy and run this with Claude Code Task tool (model: haiku)${NC}\n"

read -p "Press Enter when you've run Test 2 and are ready for Test 3..."

# Test 3
echo -e "\n${GREEN}${BOLD}Test 3: RPA Abbreviation${NC}"
echo -e "${BLUE}Expected: Should recognize RPA=ReleasePlanAdmission, answer 'platform team creates it'${NC}\n"

cat > /tmp/konflux-test-3.txt <<'EOF'
You have access to a Konflux resources skill. Use it to answer this question.

=== SKILL CONTENT START ===
EOF

cat "$SKILL_FILE" >> /tmp/konflux-test-3.txt

cat >> /tmp/konflux-test-3.txt <<'EOF'
=== SKILL CONTENT END ===

IMPORTANT: This is a real user question, not a test.

User question: "Do I create the RPA or does the platform team create it?"

After your answer, add:

INTERPRETATION:
- What does "RPA" mean?
- Who creates it according to the skill?
- Confidence level?
EOF

echo -e "${YELLOW}Test prompt saved to: /tmp/konflux-test-3.txt${NC}"
echo -e "${YELLOW}Copy and run this with Claude Code Task tool (model: haiku)${NC}\n"

read -p "Press Enter when complete..."

echo -e "\n${GREEN}${BOLD}All test prompts generated!${NC}"
echo -e "${BLUE}Review the results and compare against expected outcomes.${NC}\n"
