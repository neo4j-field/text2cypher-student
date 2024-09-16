.PHONY: all format lint test tests free_tests integration_tests help

# Default target executed when no arguments are given to make.
all: help

test:
	poetry run python3 -m pytest tests

test_integration:
	poetry run pytest python3 -m tests/integration

test_unit:
	poetry run pytest python3 -m tests/unit

init:
	poetry install --with dev, ui
	pre-commit install
	poetry run python3 -m pip install -U --no-cache-dir  \
            --config-settings="--global-option=build_ext" \
            --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
            --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
            pygraphviz


######################
# LINTING AND FORMATTING
######################

format:
	poetry run ruff format
	poetry run ruff check --select I . --fix


######################
# HELP
######################

help:
	@echo '----'
	@echo 'init........................ - initialize the repo for development'
	@echo 'format...................... - run code formatters'
	@echo 'test........................ - run all unit and integration tests'
	@echo 'test_unit................... - run all free unit tests'
	@echo 'test_integration............ - run all integration tests'
