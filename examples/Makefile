SHELL = /bin/bash
EXAMPLES := $(patsubst %/,%,$(filter-out wip/,$(shell echo */)))
EXAMPLES_ALL := $(EXAMPLES:%=%.all)
EXAMPLES_CLEAN := $(EXAMPLES:%=%.clean)
WIP_EXAMPLES := $(patsubst %/,%,$(shell echo wip/*/))
WIP_EXAMPLES_ALL := $(WIP_EXAMPLES:%=%.all)
WIP_EXAMPLES_CLEAN := $(WIP_EXAMPLES:%=%.clean)
MYS ?= PYTHONPATH=$(CURDIR)/.. python3 -m mys

.PHONY: all clean $(EXAMPLES) $(WIP_EXAMPLES)

# For examples that works.
define OK_template
$1.all:
	cd $1 && env MYS="$(MYS)" $(MYS) $2 $(ARGS)
endef

# For wip examples.
define WIP_template
$1.all:
	cd $1 && ! env MYS="$(MYS)" $(MYS) $2 $(ARGS)
endef

all: $(EXAMPLES_ALL) $(WIP_EXAMPLES_ALL)

define TARGET_template
$1: $1.all
endef
$(foreach name,$(EXAMPLES) $(WIP_EXAMPLES),$(eval $(call TARGET_template,$(name))))

clean: $(EXAMPLES_CLEAN) $(WIP_EXAMPLES_CLEAN)

$(eval $(call OK_template,brainfuck, build))
$(eval $(call OK_template,callbacks, build))
$(eval $(call OK_template,default_and_named_parameters,run))
$(eval $(call OK_template,embedded_cpp,run))
$(eval $(call OK_template,enums,run))
$(eval $(call OK_template,errors,run))

fibonacci.all:
	cd fibonacci && env MYS="$(MYS)" $(MYS) run
	cd fibonacci && env MYS="$(MYS)" $(MYS) test

$(eval $(call OK_template,fizz_buzz,run))
$(eval $(call OK_template,generics,run))

hello_world.all:
	cd hello_world && env MYS="$(MYS)" $(MYS) run
	cd hello_world && env MYS="$(MYS)" $(MYS) test

$(eval $(call OK_template,pattern_matching,run))
$(eval $(call OK_template,pi,run))
$(eval $(call OK_template,private_and_public,run))
$(eval $(call OK_template,string_formatting,run))
$(eval $(call OK_template,traits,run))
$(eval $(call WIP_template,wip/classes,build))

wip/concurrency.all:
	echo todo

wip/hn_top.all:
	echo todo

$(eval $(call WIP_template,wip/linked_list,build))

wip/local_variables.all:
	echo todo

$(eval $(call WIP_template,wip/message_passing,build))

wip/poll.all:
	echo todo

wip/regular_expressions.all:
	echo todo

wip/tcp.all:
	echo todo

wip/udp.all:
	echo todo

$(EXAMPLES_CLEAN) $(WIP_EXAMPLES_CLEAN):
	cd $(basename $@) && env MYS="$(MYS)" $(MYS) clean
