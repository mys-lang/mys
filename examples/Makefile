MYS ?= PYTHONPATH=$(shell readlink -f ..) python3 -m mys

all:
	cd exceptions && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) run
	cd fibonacci && env MYS="$(MYS)" $(MYS) run
	cd embedded_cpp && env MYS="$(MYS)" $(MYS) run
	cd wip/private_and_public && ! env MYS="$(MYS)" $(MYS) run
	cd wip/brainfuck && env MYS="$(MYS)" $(MYS) build || true
	cd wip/brainfuck && cp main.mys.cpp build/transpiled
	cd wip/brainfuck && env MYS="$(MYS)" $(MYS) build
