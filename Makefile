NAME = timetrack2
VERSION = 1.0.3

PYTHON_PACKAGE = tt
CONSOLE_SCRIPTS = $(VIRTUALENV)/bin/tt

TESTRUNNER_OPTS = --ignore=$(VIRTUALENV) -vv
LINTER_OPTS = --exclude=$(VIRTUALENV)

DOC_SOURCES = $(DOC)/sources/changelog.rst \
	      $(DOC)/sources/developers_guide.rst \
	      $(DOC)/sources/index.rst \
	      $(DOC)/sources/license.rst \
	      $(DOC)/sources/users_guide.rst

DOC_GENERATED = $(DOC)/$(PYTHON_PACKAGE).rst \
		$(DOC)/$(PYTHON_PACKAGE).test.rst \
		$(DOC)/modules.rst

DOC_TARGETS = $(DOC)/_build/html \
	      $(DOC)/_build/singlehtml \
	      $(DOC)/_build/man

include Build.mk
