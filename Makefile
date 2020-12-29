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
	$(MAKE) -C mys/lib clean
	rm -rf test_* .test_* htmlcov build .coverage

lib: pylib lib1 lib2 lib3 lib4 lib5 lib6 lib7 lib8 lib9

pylib:
	$(PYTHON) ./setup.py build_ext -j16
	cp build/lib*/mys/parser/_ast* mys/parser

lib1:
	$(MAKE) -C mys/lib O=3
lib2:
	$(MAKE) -C mys/lib O=s
lib3:
	$(MAKE) -C mys/lib O=0
lib4:
	$(MAKE) -C mys/lib O=3 TEST=1
lib5:
	$(MAKE) -C mys/lib O=s TEST=1
lib6:
	$(MAKE) -C mys/lib O=0 TEST=1
lib7:
	$(MAKE) -C mys/lib O=3 APPLICATION=1
lib8:
	$(MAKE) -C mys/lib O=s APPLICATION=1
lib9:
	$(MAKE) -C mys/lib O=0 APPLICATION=1
