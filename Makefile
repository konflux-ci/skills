.PHONY: all lint validate test test-only generate clean help install

CLAUDELINT_IMAGE := ghcr.io/stbenjam/claudelint:latest

# Number of parallel workers for test generation
WORKERS := 8

# Additional pytest arguments (e.g., PYTEST_ARGS="-x" to stop at first failure)
PYTEST_ARGS :=

# Default target - runs lint, generate, and test
all: validate generate test-only

help:
	@echo "Available targets:"
	@echo "  make              - Run linting + generate + tests (default)"
	@echo "  make all          - Same as default (lint + generate + tests)"
	@echo "  make install      - Install Python dependencies (pytest, etc.)"
	@echo "  make lint         - Run claudelint validation (strict mode)"
	@echo "  make validate     - Alias for lint"
	@echo "  make test         - Run lint validation + skill tests (skip generate)"
	@echo "  make test-only    - Run only skill tests (skip lint and generate)"
	@echo "  make generate     - Generate test results by invoking Claude"
	@echo "  make clean        - Remove all generated test results"
	@echo ""
	@echo "Test runner options:"
	@echo "  make test SKILL=<name>         - Run tests for specific skill"
	@echo "  make generate SKILL=<name>     - Generate results for specific skill"
	@echo "  make test WORKERS=N            - Use N parallel workers (default: 8)"
	@echo "  make test PYTEST_ARGS='<args>' - Pass additional pytest arguments"
	@echo ""
	@echo "Examples:"
	@echo "  make test SKILL=understanding-konflux-resources"
	@echo "  make generate WORKERS=4"
	@echo "  make test PYTEST_ARGS='-x'     # Stop at first failure"
	@echo "  make test PYTEST_ARGS='-v'     # Verbose output"
	@echo "  make test PYTEST_ARGS='-x -v'  # Stop at first failure with verbose"

install:
	@echo "Installing Python dependencies..."
	@pip install -r requirements.txt
	@echo "✓ Dependencies installed!"

lint: validate

validate:
	@echo "Running claudelint validation..."
	@docker run --rm -v $(PWD):/workspace:Z -w /workspace --user $(shell id -u):$(shell id -g) $(CLAUDELINT_IMAGE) --strict || \
		(echo "✗ Validation failed!" && exit 1)
	@echo "✓ Validation passed!"

test: validate test-only

test-only:
	@echo "Running skill tests with pytest..."
	@if python3 -c "import xdist" 2>/dev/null; then \
		pytest test/ -n $(WORKERS) -m test $(if $(SKILL),--skill $(SKILL)) $(PYTEST_ARGS); \
	else \
		echo "Warning: pytest-xdist not installed, running sequentially"; \
		pytest test/ -m test $(if $(SKILL),--skill $(SKILL)) $(PYTEST_ARGS); \
	fi

generate:
	@echo "Generating test results with pytest..."
	@if python3 -c "import xdist" 2>/dev/null; then \
		echo "Using $(WORKERS) parallel workers..."; \
		pytest test/ -n $(WORKERS) -m generate $(if $(SKILL),--skill $(SKILL)) $(PYTEST_ARGS); \
	else \
		echo "Warning: pytest-xdist not installed, running sequentially"; \
		pytest test/ -m generate $(if $(SKILL),--skill $(SKILL)) $(PYTEST_ARGS); \
	fi

clean:
	@echo "Removing all test results..."
	@find . -path '*/tests/results/*.txt' -type f -delete
	@echo "✓ Test results removed"
