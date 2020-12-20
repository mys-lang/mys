MYS ?= PYTHONPATH=$(shell readlink -f ..) python3 -m mys

.PHONY: all
.PHONY: embedded_cpp
.PHONY: fizz_buzz
.PHONY: pi
.PHONY: string_formatting
.PHONY: traits
.PHONY: brainfuck
.PHONY: default_and_named_parameters
.PHONY: generics
.PHONY: message_passing
.PHONY: private_and_public

SHELL = /bin/bash

all:
	$(MAKE) embedded_cpp
	cd exceptions && env MYS="$(MYS)" $(MYS) run
	cd fibonacci && env MYS="$(MYS)" $(MYS) run
	cd fibonacci && env MYS="$(MYS)" $(MYS) test
	$(MAKE) fizz_buzz
	cd hello_world && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) test
	$(MAKE) pi
	$(MAKE) string_formatting
	$(MAKE) traits
	$(MAKE) brainfuck
	cd wip/callbacks && ! env MYS="$(MYS)" $(MYS) build
	cd wip/classes && ! env MYS="$(MYS)" $(MYS) build
	$(MAKE) default_and_named_parameters
	$(MAKE) generics
	cd wip/linked_list && ! env MYS="$(MYS)" $(MYS) build
	$(MAKE) message_passing
	$(MAKE) private_and_public

embedded_cpp:
	cd embedded_cpp && env MYS="$(MYS)" $(MYS) run

fizz_buzz:
	cd fizz_buzz && env MYS="$(MYS)" $(MYS) run

pi:
	cd pi && env MYS="$(MYS)" $(MYS) run

string_formatting:
	cd string_formatting && env MYS="$(MYS)" $(MYS) run

traits:
	cd traits && env MYS="$(MYS)" $(MYS) run

brainfuck:
	cd brainfuck && env MYS="$(MYS)" $(MYS) build
	# ./brainfuck/build/app

message_passing:
	cd wip/message_passing && ! env MYS="$(MYS)" $(MYS) build
	# mkdir -p wip/message_passing/build/transpiled/include/message_passing
	# mkdir -p wip/message_passing/build/transpiled/src/message_passing
	# cd wip/message_passing && cp *.hpp build/transpiled/include/message_passing
	# cd wip/message_passing && cp *.cpp build/transpiled/src/message_passing
	# cd wip/message_passing && env MYS="$(MYS)" $(MYS) build || true

private_and_public:
	cd private_and_public && env MYS="$(MYS)" $(MYS) run

default_and_named_parameters:
	cd wip/default_and_named_parameters && ! env MYS="$(MYS)" $(MYS) build

generics:
	cd wip/generics && ! env MYS="$(MYS)" $(MYS) build

lint:
	cd exceptions && $(MYS) lint
	cd hello_world && $(MYS) lint
	cd fibonacci && $(MYS) lint
	cd embedded_cpp && $(MYS) lint
	cd wip/private_and_public && $(MYS) lint
	cd brainfuck && $(MYS) lint
