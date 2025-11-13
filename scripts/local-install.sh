#!/bin/bash
# Install skills from this repo into ~/.claude/skills/ using symlinks
# This allows rapid development and testing of skills

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"
SKILLS_SOURCE_DIR="${REPO_DIR}/skills"

# Skills to exclude from installation (test/internal skills)
EXCLUDED_SKILLS=("self-test-skill-invocation")

echo "Installing skills from ${REPO_DIR} to ${CLAUDE_SKILLS_DIR}..."

# Create ~/.claude/skills/ if it doesn't exist
if [ ! -d "${CLAUDE_SKILLS_DIR}" ]; then
    echo "Creating ${CLAUDE_SKILLS_DIR}..."
    mkdir -p "${CLAUDE_SKILLS_DIR}"
fi

# Find all skill directories (those containing SKILL.md)
installed_count=0
skipped_count=0

# Process each skill directory
while IFS= read -r -d '' skill_dir; do
    skill_name="$(basename "${skill_dir}")"

    # Skip excluded skills
    if [[ " ${EXCLUDED_SKILLS[*]} " =~ " ${skill_name} " ]]; then
        continue
    fi

    target_link="${CLAUDE_SKILLS_DIR}/${skill_name}"

    # Check if link already exists and points to the same location
    if [ -L "${target_link}" ]; then
        existing_target="$(readlink -f "${target_link}")"
        new_target="$(readlink -f "${skill_dir}")"

        if [ "${existing_target}" = "${new_target}" ]; then
            echo "  ✓ ${skill_name} (already installed)"
            skipped_count=$((skipped_count + 1))
            continue
        else
            echo "  ⚠ ${skill_name} (symlink exists, pointing to different location)"
            echo "    Current: ${existing_target}"
            echo "    Wanted:  ${new_target}"
            echo "    Run 'make local-uninstall' first to clean up, then retry"
            continue
        fi
    elif [ -e "${target_link}" ]; then
        echo "  ⚠ ${skill_name} (file/directory exists, not a symlink - skipping)"
        continue
    fi

    # Create symlink
    ln -s "${skill_dir}" "${target_link}"
    echo "  + ${skill_name}"
    installed_count=$((installed_count + 1))
done < <(find "${SKILLS_SOURCE_DIR}" -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/SKILL.md' \; -print0 2>/dev/null || true)

echo ""
echo "Summary:"
echo "  Installed: ${installed_count}"
echo "  Already installed: ${skipped_count}"
echo "  Total skills: $((installed_count + skipped_count))"
echo ""
echo "Skills are now available in Claude Code!"
echo "Changes to skills in ${REPO_DIR} will be immediately reflected."
