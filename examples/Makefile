MYS ?= PYTHONPATH=$(shell readlink -f ..) python3 -m mys

all:
	cd exceptions && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) run
	cd private_and_public && env MYS="$(MYS)" $(MYS) run || true
	cd fibonacci && env MYS="$(MYS)" $(MYS) run
	cd embedded_cpp && env MYS="$(MYS)" $(MYS) run
