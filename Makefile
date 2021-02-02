.PHONY: docs

ifneq ($(shell which python3),)
PYTHON = python3
else
ifneq ($(shell which python),)
PYTHON = python
else
$(warning Python not found. Neither python nor python3 was found.)
endif
endif

ifneq ($(shell which ccache),)
CCACHE := $(patsubst %,% ,ccache)
endif

COVERAGE = $(PYTHON) -m coverage
TEST_COVERAGE = env MYS="PYTHONPATH=$(CURDIR) $(COVERAGE) run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" $(COVERAGE) run -p --source=mys --omit="**/mys/parser/**" -m unittest
TEST = env PYTHONPATH=$(CURDIR) $(PYTHON) -m unittest
COMBINE = $(COVERAGE) combine -a $$(find . -name ".coverage.*")

all: test-parallel lint style
	$(MAKE) -C examples all

test-coverage: c-extension
	rm -f $$(find . -name ".coverage*")
	+$(TEST_COVERAGE) $(ARGS)
	$(COMBINE)
	$(COVERAGE) html
	$(COVERAGE) annotate --directory textcov

test: c-extension
	+$(TEST) $(ARGS)

test-install:
	rm -rf install
	rm -rf dist
	$(PYTHON) setup.py build sdist
	mkdir -p install
	cd install && \
	    tar xf ../dist/*.tar.gz --strip-components=1 && \
	    $(PYTHON) setup.py install --prefix install
	+cd install/install && \
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
	env CC="$(CCACHE)gcc" $(PYTHON) setup.py build_ext -b . -j 4

TEST_FILES := $(shell ls tests/test_*.py)

$(TEST_FILES:%=%.parallel): c-extension
	+$(TEST) $(basename $@)

test-parallel: $(TEST_FILES:%=%.parallel)

$(TEST_FILES:%=%.parallel-coverage): c-extension remove-coverage
	+$(TEST_COVERAGE) $(basename $@)

remove-coverage:
	rm -f $$(find . -name ".coverage*")

test-parallel-coverage: $(TEST_FILES:%=%.parallel-coverage)
	$(COMBINE)
	$(COVERAGE) html
	$(COVERAGE) annotate --directory textcov
	@echo
	@echo "Open $$(readlink -f htmlcov/index.html) in a web browser."
	@echo

lint:
	pylint $$(git ls-files "*.py" \
	    | grep -v "docs/\|publish/setup.py\|parser/ast.py\|coverage/")

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
	@echo "test-coverage              Same at 'test' but with code coverage."
	@echo "test-parallel              Build and run all tests in parallel. Does "
	@echo "                           not use ARGS=."
	@echo "test-parallel-coverage     Same as 'test-parallel' but with code"
	@echo "                           coverage."
	@echo "test-install               Create a dummy release and perform basic"
	@echo "                           tests on it."
	@echo "lint                       Lint the code."
	@echo "style                      Style the code."
	@echo "docs                       Build the documentation."
	@echo
	@echo "NOTE: Always use -j <number> for faster execution!"
	@echo
