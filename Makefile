include Makefile.config
-include Makefile.custom.config

all: install serve

install:
	test -d $(VENV) || virtualenv $(VENV)
	$(PIP) install --upgrade --no-cache pip setuptools -e .[test]

install-dev:
	$(PIP) install --upgrade devcore

clean:
	rm -fr dist

clean-install: clean
	rm -fr $(VENV)
	rm -fr *.egg-info

lint:
	$(PYTEST) $(PYTEST_ARGS) --flake8 -m flake8 $(PROJECT_NAME).py tests
	$(PYTEST) $(PYTEST_ARGS) --isort -m isort $(PROJECT_NAME).py tests

check-python:
	$(PYTEST) $(PYTEST_ARGS) --cov $(PROJECT_NAME) --cov tests

check-outdated:
	$(PIP) list --outdated --format=columns

check: check-python check-outdated

build:

env:
	$(RUN)

run:
	$(VENV)/bin/$(PROJECT_NAME).py

serve: run
