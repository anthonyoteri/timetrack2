PYTHON ?= python3.6

ifndef PYTHON_PACKAGE
$(error PYTHON_PACKAGE not set)
endif

ifndef NAME
$(error NAME not set)
endif

ifndef VERSION
$(error VERSION not set)
endif

VIRTUALENV ?= env
DIST ?= dist
DOC ?= doc

CONSOLE_SCRIPTS ?=

TESTRUNNER ?= bin/py.test
TESTRUNNER_OPTS ?= --ignore=$(VIRTUALENV)

LINTER ?= bin/flake8
LINTER_OPTS ?= --exclude=$(VIRTUALENV)

DOC_SOURCES ?= $(DOC)/sources/index.rst \
	       $(DOC)/sources/changelog.rst

DOC_GENERATED ?= $(DOC)/$(PYTHON_PACKAGE).rst \
		$(DOC)/$(PYTHON_PACKAGE).test.rst \
		$(DOC)/modules.rst

DOC_TARGETS ?= $(DOC)/_build/html

DIST_TARGETS ?= $(DIST)/$(NAME)-$(VERSION).tar.gz \
	        $(DIST)/$(NAME)-$(VERSION)*.whl


##### ENVIRONMENT TARGETS #####


$(VIRTUALENV): $(VIRTUALENV)/bin/activate

$(VIRTUALENV)/bin/activate: requirements.txt
	test -d $(VIRTUALENV) || virtualenv $(VIRTUALENV) --python=$(PYTHON)
	$(VIRTUALENV)/bin/pip install -Ur requirements.txt
	touch $(VIRTUALENV)/bin/activate

.PHONY: $(VIRTUALENV)-clean
$(VIRTUALENV)-clean:
	rm -rf $(VIRTUALENV)

.PHONY: clean
clean:
	$(MAKE) $(DOC)-clean
	$(MAKE) $(DIST)-clean
	$(MAKE) $(VIRTUALENV)-clean
	rm -rf \
	  build \
	  *egg-info* \
	  .eggs \
	  .pytest.cache \
	  .cache
	find . -name '*.py[co]' -delete

.PHONY: dev
dev: $(CONSOLE_SCRIPTS)

$(CONSOLE_SCRIPTS): $(PYTHON_PACKAGE) setup.py | $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -e .
	touch $@

.PHONY: dev-clean
dev-clean:
	test -x $(VIRTUALENV)/bin/pip && $(VIRTUALENV)/bin/pip uninstall -y $(NAME)
	-rm -rf $(CONSOLE_SCRIPTS)


##### DISTRIBUTION TARGETS #####


.PHONY: $(DIST)
$(DIST): $(DIST_TARGETS) $(DIST)/$(DOC)

$(DIST_TARGETS): setup.py $(PYTHON_PACKAGE) | $(VIRTUALENV)

$(DIST)/$(NAME)-$(VERSION).tar.gz:
	$(VIRTUALENV)/bin/python setup.py sdist
	touch $@

$(DIST)/$(NAME)-$(VERSION)%.whl:
	$(VIRTUALENV)/bin/python setup.py bdist_wheel
	touch $@

$(DIST)/$(DOC): $(DOC_TARGETS)
	mkdir -p $@
	cp -a $^ $@
	touch $@

.PHONY: $(DIST)-clean
$(DIST)-clean:
	-rm -rf $(DIST)


##### DOCUMENTATION TARGETS #####


.PHONY: $(DOC)
$(DOC): $(DOC_TARGETS)

$(VIRTUALENV)/bin/sphinx-apidoc: $(VIRTUALENV) requirements-doc.txt
	$(VIRTUALENV)/bin/pip install -Ur requirements-doc.txt

$(DOC_GENERATED): $(PYTHON_PACKAGE) $(DOC)/dependencies.rst | $(VIRTUALENV)/bin/sphinx-apidoc
	$(VIRTUALENV)/bin/sphinx-apidoc -o $(DOC)/ $(PYTHON_PACKAGE)
	touch $(DOC_GENERATED)

$(DOC)/dependencies.rst: | $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip list --format columns | grep '\-\-\-' | sed 's/\-/=/g' > /tmp/_table_header.rst
	echo "DEPENDENCIES\n============\n\n" > $@
	cat /tmp/_table_header.rst >> $@
	$(VIRTUALENV)/bin/pip list --format columns | grep -v $(CURDIR) >> $@
	cat /tmp/_table_header.rst >> $@

$(DOC)/_build_root: $(DOC_GENERATED) $(DOC)/dependencies.rst $(DOC_SOURCES) $(DOC)/conf.py
	rm -rf $(DOC)/_build_root && mkdir -p $(DOC)/_build_root $(DOC)/_build_root/_static
	cp $^ $(DOC)/_build_root
	touch $@

$(DOC_TARGETS): $(DOC)/_build_root $(DOC)/Makefile | $(VIRTUALENV)/$(TESTRUNNER)
	$(MAKE) -C $(DOC) $(notdir $@)

.PHONY: $(DOC)-clean
$(DOC)-clean:
	-rm -rf $(DOC)/_build_root $(DOC)/_build $(DOC_GENERATED) $(DOC)/dependencies.rst


##### TESTING TARGETS #####


.PHONY: check
check: $(VIRTUALENV)/$(LINTER)
	@$(VIRTUALENV)/$(LINTER) $(LINTER_OPTS) $(PYTHON_PACKAGE)

$(VIRTUALENV)/$(LINTER): requirements-lint.txt | $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -Ur $<

.PHONY: test
test: $(VIRTUALENV)/$(TESTRUNNER)
	$(VIRTUALENV)/$(TESTRUNNER) $(TESTRUNNER_OPTS) $(PYTHON_PACKAGE)

$(VIRTUALENV)/$(TESTRUNNER): requirements-test.txt | $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -Ur $<

.PHONY: check-deps
check-deps: | $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip list --outdated --format columns


##### RELEASE / VERSIONING TARGETS #####


.PHONY: check-release
check-release:
	@egrep -q "^$(VERSION)$$" $(DOC)/sources/changelog.rst || echo "Missing changelog description for $(VERSION)"
	@egrep -q "^__VERSION__ = '$(VERSION)'" $(PYTHON_PACKAGE)/__init__.py || echo "Missing version $(VERSION) in python package"

.PHONY: release
release: $(PYTHON_PACKAGE)/__init__.py
	$(MAKE) check-release

.PHONY: $(PYTHON_PACKAGE)/__init__.py
$(PYTHON_PACKAGE)/__init__.py:
	sed -i -e "s/^__VERSION__ = '.*'/__VERSION__ = '$(VERSION)'/" $@
