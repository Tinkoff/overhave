CODE = overhave
TESTS = tests
ALL = $(CODE) $(TESTS)
VENV ?= .venv

pre-init:
	sudo apt install python3.8 python3.8-venv python3.8-dev python3.8-distutils gcc\
        libsasl2-dev libldap2-dev libssl-dev libpq-dev g++ libgnutls28-dev

init:
	python3.8 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

precommit-install:
	@git init
	echo '#!/bin/sh\ntox\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

build:
	docker-compose build base
	docker-compose build code

build-test: build
	docker-compose build test-base
	docker-compose build test

test:
	docker-compose up -d db
	$(VENV)/bin/poetry run pytest --cov=$(CODE) --cov-fail-under=60

lint:
	$(VENV)/bin/poetry run black --skip-string-normalization --check $(ALL)
	$(VENV)/bin/poetry run flake8helled --jobs 4 --format=stat --show-source $(ALL)
	$(VENV)/bin/poetry run mypy $(ALL)
	$(VENV)/bin/poetry run pytest --dead-fixtures --dup-fixtures

pretty:
	$(VENV)/bin/poetry run isort $(ALL)
	$(VENV)/bin/poetry run black --skip-string-normalization $(ALL)

clear-cache:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf dist
	rm .coverage
