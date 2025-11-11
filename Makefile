.PHONY: all lint validate test test-only generate clean help

CLAUDELINT_IMAGE := ghcr.io/stbenjam/claudelint:latest

# Default target - runs lint, generate, and test
all: validate generate test-only

help:
	@echo "Available targets:"
	@echo "  make              - Run linting + generate + tests (default)"
	@echo "  make all          - Same as default (lint + generate + tests)"
	@echo "  make lint         - Run claudelint validation (strict mode)"
	@echo "  make validate     - Alias for lint"
	@echo "  make test         - Run lint validation + skill tests (skip generate)"
	@echo "  make test-only    - Run only skill tests (skip lint and generate)"
	@echo "  make generate     - Generate test results by invoking Claude"
	@echo "  make clean        - Remove all generated test results"
	@echo ""
	@echo "Test runner options:"
	@echo "  make test SKILL=<name>      - Run tests for specific skill"
	@echo "  make generate SKILL=<name>  - Generate results for specific skill"

lint: validate

validate:
	@echo "Running claudelint validation..."
	@docker run --rm -v $(PWD):/workspace:Z -w /workspace --user $(shell id -u):$(shell id -g) $(CLAUDELINT_IMAGE) --strict || \
		(echo "✗ Validation failed!" && exit 1)
	@echo "✓ Validation passed!"

test: validate test-only

test-only:
	@echo "Running skill tests..."
	@python3 test.py test $(if $(SKILL),--skill $(SKILL))

generate:
	@echo "Generating test results..."
	@python3 test.py generate $(if $(SKILL),--skill $(SKILL))

clean:
	@echo "Removing all test results..."
	@find . -path '*/tests/results/*.txt' -type f -delete
	@echo "✓ Test results removed"
