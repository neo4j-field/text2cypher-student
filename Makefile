.PHONY: all format lint test tests free_tests integration_tests help

# Default target executed when no arguments are given to make.
all: help

test:
	pytest tests

test_integration:
	poetry run pytest tests/integration

test_unit:
	poetry run pytest tests/unit

init:
	poetry install --with dev, ui
	pre-commit install

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
