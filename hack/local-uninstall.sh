#!/bin/bash
# Remove symlinked skills from ~/.claude/skills/ that point to this repo
# Only removes symlinks pointing to this repo - leaves other skills alone

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

echo "Uninstalling skills from ${REPO_DIR}..."

if [ ! -d "${CLAUDE_SKILLS_DIR}" ]; then
    echo "No skills directory found at ${CLAUDE_SKILLS_DIR}"
    exit 0
fi

removed_count=0
skipped_count=0

# Iterate over all items in ~/.claude/skills/
shopt -s nullglob  # Handle case where directory is empty
for item in "${CLAUDE_SKILLS_DIR}"/*; do
    [ -e "${item}" ] || continue  # Skip if glob didn't match anything

    skill_name="$(basename "${item}")"

    # Only process symlinks
    if [ ! -L "${item}" ]; then
        continue
    fi

    # Get the target the symlink points to
    link_target="$(readlink -f "${item}")"

    # Check if the symlink points somewhere inside our repo
    if [[ "${link_target}" == "${REPO_DIR}"* ]]; then
        rm "${item}"
        echo "  - ${skill_name}"
        removed_count=$((removed_count + 1))
    else
        skipped_count=$((skipped_count + 1))
    fi
done

echo ""
echo "Summary:"
echo "  Removed: ${removed_count}"
echo "  Kept (other skills): ${skipped_count}"

if [ ${removed_count} -eq 0 ]; then
    echo ""
    echo "No symlinks from this repo were found in ${CLAUDE_SKILLS_DIR}"
fi
