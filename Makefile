VIRTUALENV ?= env
PYTHON ?= python3.6
PREFIX ?= /usr/local

PYTHON_PACKAGE = tt
DOC = doc
DOC_TARGETS = html
LINTER = $(VIRTUALENV)/bin/flake8
LINTER_OPTS= --exclude=$(VIRTUALENV)
TESTRUNNER = $(VIRTUALENV)/bin/python setup.py test
TESTRUNNER_OPTS = --addopts "--ignore=$(VIRTUALENV) -vv"
DIST = dist

build: $(VIRTUALENV) requirements.txt $(PYTHON_PACKAGE)

$(VIRTUALENV): requirements.txt
	virtualenv $(VIRTUALENV) --python=$(PYTHON)
	$(VIRTUALENV)/bin/pip install -r $<
	$(VIRTUALENV)/bin/pip install -e .

$(DIST): build $(DOC)
	mkdir -p $(DIST)/doc
	cp -a $(DOC)/_build/html $(DIST)/doc/html
	$(VIRTUALENV)/bin/python setup.py sdist
	$(VIRTUALENV)/bin/python setup.py bdist_wheel

$(DOC): $(VIRTUALENV) requirements-doc.txt requirements-test.txt $(DOC)/*.rst $(PYTHON_PACKAGE)
	$(VIRTUALENV)/bin/pip install -r requirements-doc.txt
	$(VIRTUALENV)/bin/pip install -r requirements-test.txt
	$(VIRTUALENV)/bin/sphinx-apidoc -o $(DOC)/ $(PYTHON_PACKAGE)
	$(MAKE) -C $(DOC) $(DOC_TARGETS)
	touch $(DOC)

.PHONY: check
check: $(VIRTUALENV) requirements-lint.txt $(PYTHON_PACKAGE)
	$(VIRTUALENV)/bin/pip install -r requirements-lint.txt
	$(LINTER) $(LINTER_OPTS) $(PYTHON_PACKAGE)

.PHONY: test
test: build
	$(TESTRUNNER) $(TESTRUNNER_OPTS)

.PHONY: clean
clean:
	[ -f $(VIRTUALENV)/bin/python ] && $(MAKE) -C $(DOC) clean || true
	rm -rf $(VIRTUALENV) build $(DIST) *egg-info* .eggs .coverage
	rm -rf coverage.xml htmlcov junitxml-result.xml
	rm -rf .pytest.cache .cache
	rm -f $(DOC)/$(PYTHON_PACKAGE)*.rst $(DOC)/modules.rst
	find . -name '*.py[co]' -delete
