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
	$(PYTEST) --no-cov --flake8 -m flake8 $(PROJECT_NAME).py
	$(PYTEST) --no-cov --isort -m isort $(PROJECT_NAME).py

check-python:
	$(PYTEST) tests

check-outdated:
	$(PIP) list --outdated --format=columns

check: check-python check-outdated

build:

env:
	$(RUN)

run:
	$(VENV)/bin/$(PROJECT_NAME).py

serve: run
