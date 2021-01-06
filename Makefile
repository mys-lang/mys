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

all: test-parallel
	$(MAKE) -C examples all
	$(PYTHON) -m mys --version | wc -l | grep -c 1

test: lib
	rm -f $$(find . -name ".coverage*")
	+env MYS="PYTHONPATH=$(CURDIR) $(COVERAGE) run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" $(COVERAGE) run -p --source=mys --omit="**/mys/parser/**" -m unittest $(ARGS)
	$(COVERAGE) combine -a $$(find . -name ".coverage.*")
	$(COVERAGE) html

test-no-coverage: lib
	+env MYS="PYTHONPATH=$(CURDIR) $(PYTHON) -m mys" $(PYTHON) -m unittest $(ARGS)

test-install:
	rm -rf install
	$(PYTHON) setup.py install --prefix install
	+cd install && \
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

TEST_FILES := $(shell ls tests/test_*.py)

$(TEST_FILES:%=%.parallel-no-coverage): lib
	+env MYS="PYTHONPATH=$(CURDIR) $(PYTHON) -m mys" $(PYTHON) -m unittest \
	    $(basename $@)

test-parallel-no-coverage: $(TEST_FILES:%=%.parallel-no-coverage)

$(TEST_FILES:%=%.parallel): lib remove-coverage
	+env MYS="PYTHONPATH=$(CURDIR) $(COVERAGE) run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" $(COVERAGE) run -p --source=mys --omit="**/mys/parser/**" -m unittest $(basename $@)

remove-coverage:
	rm -f $$(find . -name ".coverage*")

test-parallel: $(TEST_FILES:%=%.parallel)
	$(COVERAGE) combine -a $$(find . -name ".coverage.*")
	$(COVERAGE) html

help:
	@echo "TARGET                     DESCRIPTION"
	@echo "---------------------------------------------------------------------"
	@echo "all                        'test-parallel' and examples."
	@echo "test                       Build and run all tests. Use ARGS= to pass"
	@echo "                           arguments to 'python -m unittest', for "
	@echo "                           example ARGS=\"-k test_mys\"."
	@echo "test-no-coverage           Same at 'test' but without code coverage."
	@echo "test-parallel              Build and run all tests in parallel. Does "
	@echo "                           not use ARGS=."
	@echo "test-parallel-no-coverage  Same as 'test-parallel' but without code"
	@echo "                           coverage."
	@echo "test-install               Create a dummy release and perform basic"
	@echo "                           tests on it."
	@echo
	@echo "NOTE: Always use -j <number> for faster execution!"
	@echo
