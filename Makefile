test: test-python
	$(MAKE) -C examples all
	python3 -m mys --version | wc -l | grep -c 1

test-python:
	env MYS="PYTHONPATH=$$(readlink -f .) python -m mys" python3 setup.py test $(ARGS)
