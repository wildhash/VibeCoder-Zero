.PHONY: help run clean test format lint install

help:
	@echo "VibeCoder-Zero - Autonomous Software Generation Entity"
	@echo ""
	@echo "Available commands:"
	@echo "  make run      - Execute VibeCoder-Zero"
	@echo "  make test     - Run tests"
	@echo "  make format   - Format code with black"
	@echo "  make lint     - Lint code with pylint"
	@echo "  make install  - Install dependencies"
	@echo "  make clean    - Clean generated files"

run:
	python3 vibecoder_zero.py

run-json:
	python3 vibecoder_zero.py --json

test:
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v; \
	else \
		echo "pytest not installed. Install with: pip install pytest"; \
		exit 1; \
	fi

format:
	@if command -v black >/dev/null 2>&1; then \
		black vibecoder_zero.py tests/; \
	else \
		echo "black not installed. Install with: pip install black"; \
		exit 1; \
	fi

lint:
	@if command -v pylint >/dev/null 2>&1; then \
		pylint vibecoder_zero.py; \
	else \
		echo "pylint not installed. Install with: pip install pylint"; \
		exit 1; \
	fi

install:
	pip3 install -r requirements.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage
