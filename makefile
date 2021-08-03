CODE = overhave
VENV ?= .venv
WORK_DIR ?= .
MIN_COVERAGE ?= 83.85
BUILD_DIR ?= dist

DOCS_DIR ?= docs
DOCS_BUILD_DIR ?= _build
DOCS_BUILDER ?= html
DOCS_INCLUDES_DIR = $(DOCS_DIR)/includes
DOCS_REFERENCES_DIR = $(DOCS_INCLUDES_DIR)/_references
SPHINXAPIDOC_OPTS = -f -d 3 --ext-autodoc

ALL = $(CODE) $(DOCS_DIR) tests demo

pre-init:
	sudo apt install python3.9 python3.9-venv python3.9-dev python3.9-distutils gcc\
        libsasl2-dev libldap2-dev libssl-dev libpq-dev g++ libgnutls28-dev

init:
	python3.9 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

precommit-install:
	@git init
	echo '#!/bin/sh\nmake lint\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

test:
	$(VENV)/bin/poetry run pytest -n auto --cov=$(CODE) --cov-fail-under=$(MIN_COVERAGE)

lint:
	$(VENV)/bin/poetry run black --check $(ALL)
	$(VENV)/bin/poetry run flake8 --jobs 4 --statistics $(ALL)
	$(VENV)/bin/poetry run mypy $(ALL) --exclude '(conftest|given_steps|then_steps|when_steps).py'
	$(VENV)/bin/poetry run pytest --dead-fixtures --dup-fixtures

pretty:
	$(VENV)/bin/poetry run isort $(ALL)
	$(VENV)/bin/poetry run black $(ALL)

tag:
	git tag $(TAG)
	git push origin $(TAG)

publish:
	$(VENV)/bin/poetry config pypi-token.pypi $(PYPI_TOKEN)
	$(VENV)/bin/poetry publish --build

build-docs:
	sphinx-apidoc -o $(DOCS_REFERENCES_DIR) $(CODE) $(SPHINXAPIDOC_OPTS)
	sphinx-build $(DOCS_DIR) $(DOCS_BUILD_DIR)/$(DOCS_BUILDER) -j 4 -b $(DOCS_BUILDER) -a -q -W
	@echo "Docs build finished. The results have been placed in '$(DOCS_BUILD_DIR)/$(DOCS_BUILDER)'"

check-package:
	$(VENV)/bin/poetry run twine check $(WORK_DIR)/$(BUILD_DIR)/*

check: test lint check-package build-docs

clear:
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache
	rm -rf ./$(BUILD_DIR)
	rm -rf ./$(DOCS_BUILD_DIR)
	rm -rf ./$(DOCS_REFERENCES_DIR)
	rm ./.coverage*

build-docker:
	docker-compose build base
	docker-compose build code

test-docker: build-docker
	docker-compose run code

up:
	docker-compose up -d db
	docker-compose up -d redis

down:
	docker-compose down -v
