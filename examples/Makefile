MYS ?= PYTHONPATH=$(shell readlink -f ..) python3 -m mys

.PHONY: all
.PHONY: brainfuck
.PHONY: message_passing
.PHONY: lint

SHELL = /bin/bash

all:
	cd exceptions && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) test
	cd fibonacci && env MYS="$(MYS)" $(MYS) run
	cd fibonacci && env MYS="$(MYS)" $(MYS) test
	cd embedded_cpp && env MYS="$(MYS)" $(MYS) run
	cd wip/private_and_public && ! env MYS="$(MYS)" $(MYS) run
	$(MAKE) brainfuck
	$(MAKE) message_passing
	$(MAKE) default_and_named_parameters
	$(MAKE) generics

brainfuck:
	cd wip/brainfuck && env MYS="$(MYS)" $(MYS) build || true
	mkdir -p wip/brainfuck/build/transpiled/src/brainfuck
	cd wip/brainfuck && cp main.mys.cpp build/transpiled/src/brainfuck
	cd wip/brainfuck && env MYS="$(MYS)" $(MYS) build

message_passing:
	cd wip/message_passing && env MYS="$(MYS)" $(MYS) build || true
	mkdir -p wip/message_passing/build/transpiled/include/message_passing
	mkdir -p wip/message_passing/build/transpiled/src/message_passing
	cd wip/message_passing && cp *.hpp build/transpiled/include/message_passing
	cd wip/message_passing && cp *.cpp build/transpiled/src/message_passing
	cd wip/message_passing && env MYS="$(MYS)" $(MYS) build

default_and_named_parameters:
	cd wip/default_and_named_parameters && env MYS="$(MYS)" $(MYS) build || true
	mkdir -p wip/default_and_named_parameters/build/transpiled/include/default_and_named_parameters
	mkdir -p wip/default_and_named_parameters/build/transpiled/src/default_and_named_parameters
	cd wip/default_and_named_parameters && cp main.mys.cpp build/transpiled/src/default_and_named_parameters
	cd wip/default_and_named_parameters && cp main.mys.hpp build/transpiled/include/default_and_named_parameters
	cd wip/default_and_named_parameters && env MYS="$(MYS)" $(MYS) run

generics:
	cd wip/generics && env MYS="$(MYS)" $(MYS) build || true
	mkdir -p wip/generics/build/transpiled/src/generics
	cd wip/generics && cp main.mys.cpp build/transpiled/src/generics
	cd wip/generics && env MYS="$(MYS)" $(MYS) run

lint:
	cd exceptions && $(MYS) lint
	cd hello_world && $(MYS) lint
	cd fibonacci && $(MYS) lint
	cd embedded_cpp && $(MYS) lint
	cd wip/private_and_public && $(MYS) lint
	cd wip/brainfuck && $(MYS) lint
