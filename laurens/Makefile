
PYPYPATH=/Users/cswords/Applications/pypy
PYTHONPATH=$(PYPYPATH):$(PYPYPATH)/rpython/

all:
	$(PYPYPATH)/pypy-c $(PYPYPATH)/rpython/bin/rpython --batch entry_point.py

tests:
	$(PYPYPATH)/pypy-c $(PYPYPATH)/rpython/bin/rpython --batch tests.py
