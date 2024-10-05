PROJECT_NAME := pyituran
VERSION := $(shell git describe --tags --always)
export VERSION

PYTHON_VERSION := 3.8
VENV_DIRECTORY := .venv

BUILD_DIR := build
DIST_DIR := dist
TEST_REPORT := report.xml
COVERAGE_REPORT := coverage.xml
SRC_FILES := $(shell find $(PROJECT_NAME) -name '*.py')
WHEEL := $(DIST_DIR)/$(PROJECT_NAME)-$(VERSION)-py3-none-any.whl

DOCKER_CMD :=
ifeq ($(wildcard /.dockerenv)$(RUNNER_OS),)
ifneq ($(shell which docker),)
  DOCKER_CMD := docker run $(if $(TERM),-it )--rm --user $(shell id -u):$(shell id -g) --volume $(PWD):$(PWD) --workdir $(PWD) python:$(PYTHON_VERSION)
endif
endif

ifneq ($(V),)
  Q :=
else
  Q := @
endif

.PHONY := clean black lint test reports build shell
.DEFAULT_GOAL := $(WHEEL)

$(VENV_DIRECTORY): requirements.txt dev-requirements.txt
	$(Q)$(DOCKER_CMD) python -m venv $(VENV_DIRECTORY)
	$(Q)$(DOCKER_CMD) $(VENV_DIRECTORY)/bin/python -m pip install -r requirements.txt -r dev-requirements.txt
	$(Q)touch $(VENV_DIRECTORY)
	
clean:
	$(Q)rm -rf $(VENV_DIRECTORY) $(BUILD_DIR) $(PROJECT_NAME).egg-info $(DIST_DIR) $(TEST_REPORT) $(COVERAGE_REPORT) .coverage .pytest_cache
	$(Q)find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	
format: $(VENV_DIRECTORY)
	$(Q)$(DOCKER_CMD) $(VENV_DIRECTORY)/bin/black -l 79 $(PROJECT_NAME) tests

lint: $(VENV_DIRECTORY)
	$(Q)$(DOCKER_CMD) $(VENV_DIRECTORY)/bin/flake8 $(PROJECT_NAME) tests
	$(Q)$(DOCKER_CMD) $(VENV_DIRECTORY)/bin/black -l 79 --check --diff $(PROJECT_NAME) tests

test: $(VENV_DIRECTORY)
	$(Q)$(DOCKER_CMD) $(VENV_DIRECTORY)/bin/pytest -v --cov=$(PROJECT_NAME) --junitxml=$(TEST_REPORT) --cov-report=xml:$(COVERAGE_REPORT) --cov-report=term tests

$(WHEEL): $(VENV_DIRECTORY) $(SRC_FILES)
	$(Q)$(DOCKER_CMD) $(VENV_DIRECTORY)/bin/python setup.py bdist_wheel

shell: $(VENV_DIRECTORY)
	$(Q)$(DOCKER_CMD) /bin/bash -c "source $(VENV_DIRECTORY)/bin/activate && /bin/bash"
