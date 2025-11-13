# Working with Provenance

Skill for navigating Konflux build provenance attestations to trace container images back to their source code and build logs.

## Purpose

When debugging Konflux builds, you often need to work backwards from a container image to find:
- The build logs (to debug missing SBOMs, failed tasks, etc.)
- The source commit (to see what changed)
- The git repository (to clone and investigate)
- The build parameters (to reproduce issues)

This skill provides helper scripts and patterns for extracting this information from SLSA provenance attestations using `cosign` and `jq`.

## What This Skill Provides

1. **Helper scripts** for common provenance operations:
   - `build-log-link.sh` - Extract pipeline log URL
   - `build-commit-link.sh` - Extract git commit URL (handles GitHub/GitLab)
   - `build-git-repo.sh` - Extract repository URL
   - `build-origin-pullspec.sh` - Extract original image pullspec with commit SHA

2. **Quick reference table** for jq expressions to extract specific fields from provenance

3. **Common workflows** for debugging and tracing builds

## Use Cases

- **Missing SBOM investigation**: Trace image → build logs to see if SBOM task ran
- **Code change investigation**: Trace image → commit to see what changed recently
- **Security verification**: Definitively verify which source code produced an image
- **Build reproduction**: Extract exact build parameters to reproduce locally

## Testing

All scenarios tested with TDD methodology:
- ✅ Trace missing SBOM to logs (3 samples)
- ✅ Trace build to commit (3 samples)
- ✅ Verify image source (3 samples)
- ✅ Extract pipeline logs (3 samples)
- ✅ Extract git repository (3 samples)
- ✅ Negative test: Don't apply to non-Konflux images (3 samples)

**Total: 18/18 scenarios passing**

Run tests: `make test SKILL=working-with-provenance`

## Example Usage

```bash
# Find build logs for debugging
./scripts/build-log-link.sh quay.io/org/image:tag

# Find source commit
./scripts/build-commit-link.sh quay.io/org/image:tag

# Trace to repository
./scripts/build-git-repo.sh quay.io/org/image:tag
```

## Requirements

- `cosign` CLI tool
- `jq` for JSON parsing
- Access to Konflux-built images (quay.io/redhat-user-workloads/*)

## Installation

This skill is available in the Konflux Skills marketplace. It will be automatically discovered when installed via the marketplace.

## Version

1.0.0 - Initial release

## Author

Konflux CI Team
