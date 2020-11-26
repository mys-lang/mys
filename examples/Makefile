MYS ?= PYTHONPATH=$(shell readlink -f ..) python3 -m mys

.PHONY: all
.PHONY: brainfuck
.PHONY: message_passing
.PHONY: lint
.PHONY: fizz_buzz
.PHONY: pi
.PHONY: embedded_cpp
.PHONY: string_formatting

SHELL = /bin/bash

all:
	$(MAKE) fizz_buzz
	cd exceptions && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) test
	cd fibonacci && env MYS="$(MYS)" $(MYS) run
	cd fibonacci && env MYS="$(MYS)" $(MYS) test
	$(MAKE) pi
	$(MAKE) embedded_cpp
	cd wip/private_and_public && ! env MYS="$(MYS)" $(MYS) run
	$(MAKE) brainfuck
	$(MAKE) message_passing
	$(MAKE) default_and_named_parameters
	$(MAKE) generics
	$(MAKE) string_formatting

fizz_buzz:
	cd fizz_buzz && env MYS="$(MYS)" $(MYS) run

pi:
	cd pi && env MYS="$(MYS)" $(MYS) run

embedded_cpp:
	cd embedded_cpp && env MYS="$(MYS)" $(MYS) run

string_formatting:
	cd string_formatting && env MYS="$(MYS)" $(MYS) run

brainfuck:
	cd wip/brainfuck && env MYS="$(MYS)" $(MYS) build || true
	mkdir -p wip/brainfuck/build/transpiled/src/brainfuck
	cd wip/brainfuck && cp main.mys.cpp build/transpiled/src/brainfuck
	cd wip/brainfuck && env MYS="$(MYS)" APPLICATION=yes \
	    make -f build/Makefile build/app
	# ./wip/brainfuck/build/app

message_passing:
	cd wip/message_passing && env MYS="$(MYS)" $(MYS) build || true
	mkdir -p wip/message_passing/build/transpiled/include/message_passing
	mkdir -p wip/message_passing/build/transpiled/src/message_passing
	cd wip/message_passing && cp *.hpp build/transpiled/include/message_passing
	cd wip/message_passing && cp *.cpp build/transpiled/src/message_passing
	cd wip/message_passing && env MYS="$(MYS)" $(MYS) build || true

default_and_named_parameters:
	cd wip/default_and_named_parameters && env MYS="$(MYS)" $(MYS) build || true

generics:
	cd wip/generics && env MYS="$(MYS)" $(MYS) build || true

lint:
	cd exceptions && $(MYS) lint
	cd hello_world && $(MYS) lint
	cd fibonacci && $(MYS) lint
	cd embedded_cpp && $(MYS) lint
	cd wip/private_and_public && $(MYS) lint
	cd wip/brainfuck && $(MYS) lint
