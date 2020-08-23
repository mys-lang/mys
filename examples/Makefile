MYS ?= PYTHONPATH=$(shell readlink -f ..) python3 -m mys

all:
	cd exceptions && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) run
	cd pbconfig && env MYS="$(MYS)" $(MYS) run
	cd threads && env MYS="$(MYS)" $(MYS) run
	cd private_and_public && env MYS="$(MYS)" $(MYS) run
