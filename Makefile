test: test-python
	$(MAKE) -C tests/files
	$(MAKE) -C examples

test-python:
	env MYS="PYTHONPATH=$$(readlink -f .) python -m mys" python3 setup.py test $(ARGS)
