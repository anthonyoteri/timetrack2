VIRTUALENV ?= env

all: build


build: $(VIRTUALENV)


$(VIRTUALENV):
	virtualenv $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf $(VIRTUALENV) build dist *egg-info*
	find . -name '*.py[co]' -delete
	
