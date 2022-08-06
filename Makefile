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
TEST_COVERAGE = env MYS="PYTHONPATH=$(CURDIR):$(CURDIR)/mys/pygments $(COVERAGE) run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" $(COVERAGE) run -p --source=mys --omit="**/mys/parser/**" -m pytest -q -n auto --lf
TEST = env PYTHONPATH=$(CURDIR):$(CURDIR)/mys/pygments $(PYTHON) -m pytest -q -n auto --lf
COMBINE = $(COVERAGE) combine -a $$(find . -name ".coverage.*")

all: style lint test-lib
	$(MAKE) test
	$(MAKE) docs
	$(MAKE) -C examples all

test-lib:
	$(MAKE) -C mys/lib/test

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
	$(MAKE) -C mys/lib/test clean
	rm -rf tests/build .test_* htmlcov build .coverage

c-extension:
	env CC="$(CCACHE)gcc" $(PYTHON) setup.py build_ext -b . -j 4

TEST_FILES := $(shell ls tests/test_*.py)

remove-coverage:
	rm -f $$(find . -name ".coverage*")

lint:
	pylint $$(git ls-files "*.py" \
	    | grep -v "docs/\|publish/setup.py\|parser/ast.py\|examples/wip\|mys/pygments\|doc/conf.py\|tools/")

style:
	isort --force-single-line-imports .

docs: c-extension
	$(MAKE) -C docs clean
	env PYTHONPATH=$(CURDIR):$(CURDIR)/mys/pygments:$$PYTHONPATH $(MAKE) -C docs SPHINXOPTS="-W" html
	@echo
	@echo "Open file://$(CURDIR)/docs/build/html/index.html in a web browser."
	@echo

VERSION := $(shell $(PYTHON) -c "print(open('mys/version.py').read().split('\'')[1])")
PUBLISH_ADDRESS ?= https://mys-lang.org
PUBLISH_TOKEN ?=

publish: docs
	cp -r docs/build/html .
	rm -rf $(VERSION)
	mv html $(VERSION)
	tar czf mys-$(VERSION).tar.gz $(VERSION)
ifeq ($(PUBLISH_TOKEN),)
	curl --fail -X POST --data-binary @mys-$(VERSION).tar.gz \
	    $(PUBLISH_ADDRESS)/mys-$(VERSION).tar.gz
else
	curl --fail -X POST --data-binary @mys-$(VERSION).tar.gz \
	    $(PUBLISH_ADDRESS)/mys-$(VERSION).tar.gz?token=$(PUBLISH_TOKEN)
endif

bundle: c-extension
	pyinstaller \
	    --distpath mys-$(VERSION) \
	    --add-data mys/lib:mys/lib \
	    --add-data mys/cli/templates:mys/cli/templates \
	    --add-data mys/pcre2:mys/pcre2 \
	    --add-data mys/uv:mys/uv \
	    mystic.py
	cp tools/mys.sh mys-$(VERSION)/mys
	tar czf mys-$(VERSION).tar.gz mys-$(VERSION)
