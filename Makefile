.PHONY: docs

ifneq ($(shell which coverage),)
COVERAGE = coverage
else
ifneq ($(shell which python3-coverage),)
COVERAGE = python3-coverage
else
$(warning Coverage not found)
endif
endif

ifneq ($(shell which python3),)
PYTHON = python3
else
ifneq ($(shell which python),)
PYTHON = python
else
$(warning Python not found)
endif
endif

ifneq ($(shell which ccache),)
CCACHE = ccache
endif

TEST = env MYS="PYTHONPATH=$(CURDIR) $(COVERAGE) run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" $(COVERAGE) run -p --source=mys --omit="**/mys/parser/**" -m unittest
TEST_NO_COVERAGE = env MYS="PYTHONPATH=$(CURDIR) $(PYTHON) -m mys" $(PYTHON) -m unittest
COMBINE = $(COVERAGE) combine -a $$(find . -name ".coverage.*")

all: test-parallel lint
	$(MAKE) -C examples all
	$(PYTHON) -m mys --version | wc -l | grep -c 1

test: c-extension
	rm -f $$(find . -name ".coverage*")
	+$(TEST) $(ARGS)
	$(COMBINE)
	$(COVERAGE) html

test-no-coverage: c-extension
	+$(TEST_NO_COVERAGE) $(ARGS)

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

c-extension:
	env CC="$(CCACHE) gcc" $(PYTHON) setup.py build_ext -b . -j 4

TEST_FILES := $(shell ls tests/test_*.py)

$(TEST_FILES:%=%.parallel-no-coverage): c-extension
	+$(TEST_NO_COVERAGE) $(basename $@)

test-parallel-no-coverage: $(TEST_FILES:%=%.parallel-no-coverage)

$(TEST_FILES:%=%.parallel): c-extension remove-coverage
	+$(TEST) $(basename $@)

remove-coverage:
	rm -f $$(find . -name ".coverage*")

test-parallel: $(TEST_FILES:%=%.parallel)
	$(COMBINE)
	$(COVERAGE) html

lint:
	pylint $$(git ls-files "*.py" \
	    | grep -v "docs/\|publish/setup.py\|parser/ast.py")

style:
	isort --force-single-line-imports .

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs SPHINXOPTS="-W" html
	@echo
	@echo "Open $$(readlink -f docs/build/html/index.html) in a web browser."
	@echo

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
	@echo "lint                       Lint the code."
	@echo "docs                       Build the documentation."
	@echo
	@echo "NOTE: Always use -j <number> for faster execution!"
	@echo
