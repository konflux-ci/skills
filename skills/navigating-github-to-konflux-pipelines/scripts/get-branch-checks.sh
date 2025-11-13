#!/bin/bash
# get-branch-checks.sh - Get GitHub check runs for a branch/commit
#
# Usage: get-branch-checks.sh <owner> <repo> <ref> [jq-filter]
#
# Arguments:
#   owner      - Repository owner (e.g., "konflux-ci")
#   repo       - Repository name (e.g., "yq-container")
#   ref        - Branch name or commit SHA (e.g., "main", "abc123")
#   jq-filter  - Optional jq filter to apply (e.g., '.check_runs[]')
#
# Examples:
#   # Get all check runs for main branch
#   get-branch-checks.sh konflux-ci yq-container main
#
#   # Filter for Konflux checks only
#   get-branch-checks.sh konflux-ci yq-container main '.check_runs[] | select(.name | ascii_downcase | contains("konflux"))'
#
# This script uses the read-only GitHub API endpoint:
#   GET /repos/{owner}/{repo}/commits/{ref}/check-runs
#
# Security: Read-only access to public check run information.

set -euo pipefail

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <owner> <repo> <ref> [jq-filter]" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 konflux-ci yq-container main" >&2
    echo "  $0 konflux-ci yq-container main '.check_runs[] | select(.name | contains(\"konflux\"))'" >&2
    exit 1
fi

owner="$1"
repo="$2"
ref="$3"
jq_filter="${4:-}"

# Construct API endpoint
endpoint="repos/$owner/$repo/commits/$ref/check-runs"

# Call gh api with optional jq filter
if [ -n "$jq_filter" ]; then
    gh api "$endpoint" --jq "$jq_filter"
else
    gh api "$endpoint"
fi
