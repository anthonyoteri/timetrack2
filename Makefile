VIRTUALENV ?= env
PYTHON ?= python3.6

PYTHON_PACKAGE = tt
LINTER = $(VIRTUALENV)/bin/flake8
LINTER_OPTS= --exclude=$(VIRTUALENV)
TESTRUNNER = $(VIRTUALENV)/bin/python setup.py test
TESTRUNNER_OPTS = --addopts "--ignore=$(VIRTUALENV) -vv"
all: build


build: $(VIRTUALENV)


$(VIRTUALENV):
	virtualenv $(VIRTUALENV) --python=$(PYTHON)
	$(VIRTUALENV)/bin/pip install -r requirements.txt
	$(VIRTUALENV)/bin/pip install -e .


.PHONY: check
check: $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r requirements-lint.txt
	$(VIRTUALENV)/bin/pip install -e .
	$(LINTER) $(LINTER_OPTS) $(PYTHON_PACKAGE)

test: build 
	$(VIRTUALENV)/bin/pip install -r requirements-test.txt
	$(VIRTUALENV)/bin/pip install -e .
	$(TESTRUNNER) $(TESTRUNNER_OPTS)

.PHONY: clean
clean:
	rm -rf $(VIRTUALENV) build dist *egg-info* .coverage
	rm -rf coverage.xml htmlcov junitxml-result.xml
	find . -name '*.py[co]' -delete
	
