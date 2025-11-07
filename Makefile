.PHONY: lint validate test help

CLAUDELINT_IMAGE := ghcr.io/stbenjam/claudelint:latest

help:
	@echo "Available targets:"
	@echo "  make lint      - Run claudelint validation (strict mode)"
	@echo "  make validate  - Alias for lint"
	@echo "  make test      - Run validation tests"

lint: validate

validate:
	@echo "Running claudelint validation..."
	@docker run --rm -v $(PWD):/workspace:Z -w /workspace --user $(shell id -u):$(shell id -g) $(CLAUDELINT_IMAGE) --strict || \
		(echo "✗ Validation failed!" && exit 1)
	@echo "✓ Validation passed!"

test: validate
	@echo "All tests passed!"
