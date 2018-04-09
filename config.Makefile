export PROJECT_NAME = bobslide
export PYTEST_ARGS = -c=/dev/null

# Python env
VENV = $(PWD)/.env
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python
PYTEST = $(VENV)/bin/py.test
FLASK = $(VENV)/bin/flask

GIT = /usr/bin/git

URL_PROD = https://bobslide.kozea.fr
