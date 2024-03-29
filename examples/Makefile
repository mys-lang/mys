SHELL = /bin/bash
EXAMPLES := $(patsubst %/,%,$(filter-out wip/,$(shell echo */)))
EXAMPLES_ALL := $(EXAMPLES:%=%.all)
EXAMPLES_CLEAN := $(EXAMPLES:%=%.clean)
WIP_EXAMPLES := $(patsubst %/,%,$(shell echo wip/*/))
WIP_EXAMPLES_ALL := $(WIP_EXAMPLES:%=%.all)
WIP_EXAMPLES_CLEAN := $(WIP_EXAMPLES:%=%.clean)
MYS ?= env PYTHONPATH=$(CURDIR)/.. python3 -m mys

.PHONY: all clean $(EXAMPLES) $(WIP_EXAMPLES)

# For examples that works.
define OK_template
$1.all:
	cd $1 && $(MYS) $2 $(ARGS)
endef

# For wip examples.
define WIP_template
$1.all:
	cd $1 && ! $(MYS) $2 $(ARGS)
endef

all: $(EXAMPLES_ALL) $(WIP_EXAMPLES_ALL)

define TARGET_template
$1: $1.all
endef
$(foreach name,$(EXAMPLES) $(WIP_EXAMPLES),$(eval $(call TARGET_template,$(name))))

clean: $(EXAMPLES_CLEAN) $(WIP_EXAMPLES_CLEAN)

$(eval $(call OK_template,callbacks,build))
$(eval $(call OK_template,ctrl_c,build))
$(eval $(call OK_template,default_and_named_parameters,run))
$(eval $(call OK_template,embedded_cpp,run))
$(eval $(call OK_template,enums,run))
$(eval $(call OK_template,errors,run))
$(eval $(call OK_template,fibers,build))

fibonacci.all:
	cd fibonacci && $(MYS) run
	cd fibonacci && $(MYS) test

$(eval $(call OK_template,fizz_buzz,run))
$(eval $(call OK_template,generics,run))
$(eval $(call OK_template,hash,run))

hello_world.all:
	cd hello_world && $(MYS) run
	cd hello_world && $(MYS) test

$(eval $(call OK_template,local_variables,run))
$(eval $(call OK_template,macro,run))
$(eval $(call OK_template,pattern_matching,run))
$(eval $(call OK_template,pi,run))
$(eval $(call OK_template,prechelt_phone_number_encoding,run -- dictionary.txt phone_numbers.txt))
$(eval $(call OK_template,private_and_public,run))
$(eval $(call OK_template,ray_tracing,build))
$(eval $(call OK_template,regular_expressions,run))
$(eval $(call OK_template,string_formatting,run))
$(eval $(call OK_template,the_super_tiny_compiler,test))
$(eval $(call OK_template,traceback,build -o debug))
$(eval $(call OK_template,traits,run))
$(eval $(call OK_template,optionals,run))

wip/concurrency.all:
	echo todo

wip/iterators.all:
	echo todo

$(eval $(call WIP_template,wip/linked_list,build))
$(eval $(call WIP_template,wip/message_passing,build))

wip/mocking.all:
	echo todo

wip/poll.all:
	echo todo

wip/sort_list.all:
	echo todo

$(EXAMPLES_CLEAN) $(WIP_EXAMPLES_CLEAN):
	cd $(basename $@) && $(MYS) clean
