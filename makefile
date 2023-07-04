CODE = overhave
VENV ?= .venv
WORK_DIR ?= .
MIN_COVERAGE ?= 87.1
PACKAGE_BUILD_DIR ?= dist
PYTHON_VERSION ?= 3.11

DOCS_DIR ?= docs
DOCS_BUILD_DIR ?= _build
DOCS_BUILDER ?= html
DOCS_INCLUDES_DIR = $(DOCS_DIR)/includes
DOCS_IMAGES_DIR = $(DOCS_INCLUDES_DIR)/images
COV_BADGE_SVG = $(DOCS_IMAGES_DIR)/coverage.svg
DOCS_REFERENCES_DIR = $(DOCS_INCLUDES_DIR)/_references
SPHINXAPIDOC_OPTS = -f -d 3 --ext-autodoc
MYPY_CACHE_DIR = .mypy_cache

ALL = $(CODE) $(DOCS_DIR) tests demo

JOBS ?= 4

pre-init:
	sudo apt install python$(PYTHON_VERSION) python$(PYTHON_VERSION)-venv python$(PYTHON_VERSION)-dev python$(PYTHON_VERSION)-distutils gcc\
        libsasl2-dev libldap2-dev libssl-dev libpq-dev g++ libgnutls28-dev

init:
	python$(PYTHON_VERSION) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

precommit-install:
	@git init
	echo '#!/bin/sh\nmake lint\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

test:
	$(VENV)/bin/poetry run pytest -n auto --cov=$(CODE) --cov-fail-under=$(MIN_COVERAGE)

black:
	$(VENV)/bin/poetry run black --check $(ALL)

flake8:
	$(VENV)/bin/poetry run flake8 --jobs 4 --statistics $(ALL)

perflint:
	$(VENV)/bin/poetry run perflint $(ALL) --disable=W8201,W8202,R8203,W8205

mypy:
	$(VENV)/bin/poetry run mypy --install-types --non-interactive $(ALL) --exclude '(conftest|given_steps|then_steps|when_steps).py'

pytest-lint:
	$(VENV)/bin/poetry run pytest --dead-fixtures --dup-fixtures

lint: black flake8 perflint mypy pytest-lint

parallel-lint:
	make -j $(JOBS) lint

pretty:
	$(VENV)/bin/poetry run isort $(ALL)
	$(VENV)/bin/poetry run black $(ALL)

plint: pretty lint

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

cov-badge:
	$(VENV)/bin/poetry run coverage-badge -f -o $(COV_BADGE_SVG)

check-cov-badge:
	git diff --exit-code $(COV_BADGE_SVG)  # if failed --> add to commit actual badge

check-package:
	$(VENV)/bin/poetry check
	$(VENV)/bin/poetry build  # to PACKAGE_BUILD_DIR
	$(VENV)/bin/poetry run twine check $(WORK_DIR)/$(PACKAGE_BUILD_DIR)/*

check: lint test cov-badge check-package build-docs

clear:
	rm -rf ./$(MYPY_CACHE_DIR)
	rm -rf ./.pytest_cache
	rm -rf ./$(PACKAGE_BUILD_DIR)
	rm -rf ./$(DOCS_BUILD_DIR)
	rm -rf ./$(DOCS_REFERENCES_DIR)
	rm ./.coverage*
	mkdir ./$(MYPY_CACHE_DIR)

build-docker:
	docker-compose build base
	docker-compose build code

test-docker: build-docker
	docker-compose run code

up:
	docker-compose up -d db redis

down:
	docker-compose down -v
