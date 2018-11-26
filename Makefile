PYTHON := $(shell which python3)
ENV := $(CURDIR)/env
PIP := $(ENV)/bin/pip
ENVPYTHON := $(ENV)/bin/python

default: help

help:
	@printf "\033[0;32mWelcome the the ex2calcurse repo!\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo

$(ENV):
	$(PYTHON) -m venv env
	$(PIP) install -U pip setuptools

deps: $(ENV) ## builds the virtualenv / dependacies needed to run the script
	$(PIP) install --upgrade -r requirements/base.txt

test: $(deps) ## tests the script, assumes a ex2cal.conf.test config file
	$(ENVPYTHON) watcher.py -c ex2calcurse.config.test

clean: ## removes the virtual env / directory
	rm -rf $(ENV)
