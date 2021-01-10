LIB = {mys_dir}/lib
export CCACHE_BASEDIR = {mys_dir}
export CCACHE_SLOPPINESS = pch_defines,time_macros

GCH := build/mys_pre_
MYS_CXX ?= {ccache}$(CXX)
MYS ?= mys
CFLAGS += -I$(LIB)
CFLAGS += -Ibuild/transpiled/include
# CFLAGS += -Wall
CFLAGS += -Wno-unused-variable
CFLAGS += -Wno-unused-value
CFLAGS += -Wno-return-type
# CFLAGS += -Wno-parentheses-equality
# CFLAGS += -Wno-unused-but-set-variable
CFLAGS += -Winvalid-pch
CFLAGS += -O{optimize}
CFLAGS += -std=c++17
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
CFLAGS += -fdiagnostics-color=always
ifeq ($(TEST), yes)
CFLAGS += -DMYS_TEST
OBJ_SUFFIX = test.o
GCH := $(GCH)test.hpp
else
ifeq ($(APPLICATION), yes)
CFLAGS += -DMYS_APPLICATION
GCH := $(GCH)app.hpp
else
GCH := $(GCH).hpp
endif
OBJ_SUFFIX = o
endif
LDFLAGS += -std=c++17
# LDFLAGS += -static
# LDFLAGS += -Wl,--gc-sections
LDFLAGS += -fdiagnostics-color=always
{transpiled_cpp}
{objs}
EXE = build/app
TEST_EXE = build/test

all:
	$(MAKE) -f build/Makefile build/transpile
	$(MAKE) -f build/Makefile {all_deps}

test:
	$(MAKE) -f build/Makefile build/transpile
	$(MAKE) -f build/Makefile $(TEST_EXE)

build/transpile: {transpile_srcs_paths}
	$(MYS) $(TRANSPILE_DEBUG) transpile {transpile_options} -o build/transpiled {transpile_srcs}
	touch $@

$(TEST_EXE): $(OBJ) build/mys.$(OBJ_SUFFIX)
	$(MYS_CXX) $(LDFLAGS) -o $@ $^

$(EXE): $(OBJ) build/mys.$(OBJ_SUFFIX)
	$(MYS_CXX) $(LDFLAGS) -o $@ $^

%.mys.$(OBJ_SUFFIX): %.mys.cpp $(GCH).gch
	$(MYS_CXX) $(CFLAGS) -include $(GCH) -c $< -o $@

$(GCH).gch: $(LIB)/mys.hpp
	$(MYS_CXX) $(CFLAGS) -c $< -o $@

build/mys.$(OBJ_SUFFIX): $(LIB)/mys.cpp $(GCH).gch
	$(MYS_CXX) $(CFLAGS) -include $(GCH) -c $< -o $@
