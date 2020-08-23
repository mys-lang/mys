test:
	env MYS="PYTHONPATH=$$(readlink -f .) python -m mys" python3 setup.py test
	$(MAKE) -C tests/files
	$(MAKE) -C examples
