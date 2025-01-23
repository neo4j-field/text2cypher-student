.PHONY: all format lint test tests free_tests integration_tests help

# Default target executed when no arguments are given to make.
all: help

test:
	poetry run pytest tests

test_integration:
	poetry run pytest tests/integration

test_unit:
	poetry run pytest tests/unit

init:
	poetry install --with dev, ui
	pre-commit install
	poetry run python3 -m pip install -U --no-cache-dir  \
            --config-settings="--global-option=build_ext" \
            --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
            --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
            pygraphviz

init_workshop:
	poetry config virtualenvs.in-project true
	poetry install --with workshop


######################
# LINTING AND FORMATTING
######################

format:
	poetry run ruff format
	poetry run ruff check --select I . --fix
	poetry run ruff check .


######################
# MYPY CHECK
######################

mypy:
	poetry run mypy --strict --ignore-missing-imports --allow-subclassing-any --allow-untyped-calls .


######################
# HELP
######################

help:
	@echo '----'
	@echo 'init........................ - initialize the repo for development'
	@echo 'init_workshop............... - initialize the repo for the workshop'
	@echo 'format...................... - run code formatters'
	@echo 'test........................ - run all unit and integration tests'
	@echo 'test_unit................... - run all free unit tests'
	@echo 'test_integration............ - run all integration tests'
