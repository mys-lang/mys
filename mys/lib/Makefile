CXX ?= g++

ifneq ($(TEST),)
OUTDIR = build_test_$(O)
else
ifneq ($(APPLICATION),)
OUTDIR = build_application_$(O)
else
OUTDIR = build_package_$(O)
endif
endif
CFLAGS += -I$(OUTDIR)
CFLAGS += -O$(O)
CFLAGS += -Wall
CFLAGS += -std=c++17
ifneq ($(TEST),)
CFLAGS += -DMYS_TEST
OBJ_SUFFIX = test.o
else
ifneq ($(APPLICATION),)
CFLAGS += -DMYS_APPLICATION
endif
OBJ_SUFFIX = o
endif

all: $(OUTDIR)/mys.$(OBJ_SUFFIX)

clean:
	rm -rf build_*

$(OUTDIR)/mys.hpp.gch: mys.hpp
	@mkdir -p $(dir $@)
	$(CXX) $(CFLAGS) -c $< -o $@

$(OUTDIR)/mys.$(OBJ_SUFFIX): mys.cpp $(OUTDIR)/mys.hpp.gch
	@mkdir -p $(dir $@)
	$(CXX) $(CFLAGS) -c $< -o $@
