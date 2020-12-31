ifneq ($(shell which coverage),)
COVERAGE=coverage
else
ifneq ($(shell which python3-coverage),)
COVERAGE=python3-coverage
else
$(warning Coverage not found)
endif
endif

ifneq ($(shell which python3),)
PYTHON=python3
else
ifneq ($(shell which python),)
PYTHON=python
else
$(warning Python not found)
endif
endif

test: test-python
	$(MAKE) -C examples all
	$(PYTHON) -m mys --version | wc -l | grep -c 1

test-python: lib
	env MYS="PYTHONPATH=$$(readlink -f .) $(COVERAGE) run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" $(COVERAGE) run -p --source=mys --omit="**/mys/parser/**" -m unittest $(ARGS)
	$(COVERAGE) combine -a $$(find -name ".coverage.*")
	$(COVERAGE) html

clean:
	$(MAKE) -C examples clean
	rm -rf tests/build .test_* htmlcov build .coverage

lib:
	$(PYTHON) ./setup.py build_ext -j16
	cp build/lib*/mys/parser/_ast* mys/parser
