
PYPYPATH=/Users/cswords/Applications/pypy
PYTHONPATH=$(PYPYPATH):$(PYPYPATH)/rpython/

all:
	$(PYPYPATH)/pypy-c $(PYPYPATH)/rpython/bin/rpython --batch -Ojit tests.py
