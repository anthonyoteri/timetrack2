VIRTUALENV ?= env
PYTHON ?= python3.6

PYTHON_PACKAGE = tt
LINTER = $(VIRTUALENV)/bin/flake8
LINTER_OPTS= --exclude=$(VIRTUALENV)
TESTRUNNER = $(VIRTUALENV)/bin/py.test
TESTRUNNER_OPTS = --verbose -r s --ignore=$(VIRTUALENV)
COVERAGE = $(TESTRUNNER)
COVERAGE_OPTS = --ignore=$(VIRTUALENV) --cov=$(PYTHON_PACKAGE)

all: build


build: $(VIRTUALENV)


$(VIRTUALENV):
	virtualenv $(VIRTUALENV) --python=$(PYTHON)
	$(VIRTUALENV)/bin/pip install -r requirements.txt

$(LINTER): $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r requirements-lint.txt

.PHONY: check
check: $(VIRTUALENV) $(LINTER)
	$(LINTER) $(LINTER_OPTS) $(PYTHON_PACKAGE)

$(TESTRUNNER): $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r requirements-test.txt

test: build $(TESTRUNNER)
	$(TESTRUNNER) $(TESTRUNNER_OPTS) $(tests)

.PHONY: coverage

coverage: build $(COVERAGE)
	$(COVERAGE) $(COVERAGE_OPTS) $(tests)

.PHONY: clean
clean:
	rm -rf $(VIRTUALENV) build dist *egg-info* .coverage
	find . -name '*.py[co]' -delete
	
