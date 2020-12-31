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

ifneq ($(shell which ccache),)
CCACHE=ccache
endif

test: test-python
	$(MAKE) -C examples all
	$(PYTHON) -m mys --version | wc -l | grep -c 1

test-python: lib
	env MYS="PYTHONPATH=$$(readlink -f .) $(COVERAGE) run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" $(COVERAGE) run -p --source=mys --omit="**/mys/parser/**" -m unittest $(ARGS)
	$(COVERAGE) combine -a $$(find -name ".coverage.*")
	$(COVERAGE) html

test-install:
	rm -rf install
	$(PYTHON) setup.py install --prefix install
	cd install && \
	    export PATH=$$(readlink -f bin):$$PATH && \
	    export PYTHONPATH=$$(readlink -f lib/python*/site-packages/mys-*) && \
	    which mys && \
	    mys new foo && \
	    cd foo && \
	    mys run -v && \
	    mys test -v

clean:
	$(MAKE) -C examples clean
	rm -rf tests/build .test_* htmlcov build .coverage

lib:
	env CC="$(CCACHE) gcc" $(PYTHON) setup.py build_ext -j 4
	cp build/lib*/mys/parser/_ast* mys/parser
