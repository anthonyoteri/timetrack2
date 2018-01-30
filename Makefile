VIRTUALENV ?= env
PYTHON ?= python3.6

all: build


build: $(VIRTUALENV)


$(VIRTUALENV):
	virtualenv $(VIRTUALENV) --python=$(PYTHON)
	$(VIRTUALENV)/bin/pip install -r requirements.txt

$(VIRTUALENV)/bin/flake8: $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install flake8

.PHONY: check
check: $(VIRTUALENV) $(VIRTUALENV)/bin/flake8
	$(VIRTUALENV)/bin/flake8 tt

.PHONY: clean
clean:
	rm -rf $(VIRTUALENV) build dist *egg-info*
	find . -name '*.py[co]' -delete
	
