# Tests for understanding-konflux-resources

This directory contains test scenarios and generated results for validating the skill.

## Structure

- `scenarios.yaml` - Test scenario definitions with expectations
- `results/` - Generated test results (one file per scenario sample)

## Running Tests

**Generate test results** (invokes Claude):
```bash
make generate SKILL=understanding-konflux-resources
```

**Run tests** (validates results):
```bash
make test SKILL=understanding-konflux-resources
```

## How It Works

1. `scenarios.yaml` defines test prompts and expected outcomes
2. `make generate` invokes Claude with the skill loaded, saves outputs to `results/`
3. Each result file includes a digest of the skill content on the first line
4. `make test` validates results match expectations and digest matches current skill
5. If skill content changes, tests fail until `make generate` is run again

See root `Makefile` and `test.py` for implementation details.
