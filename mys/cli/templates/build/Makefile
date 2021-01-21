LIB = {mys_dir}/lib
export CCACHE_BASEDIR = {mys_dir}
export CCACHE_SLOPPINESS = pch_defines,time_macros,include_file_mtime,include_file_ctime

GCH := build/mys_pre_
MYS_CXX ?= {ccache}$(CXX)
MYS ?= {mys}
CFLAGS += -I$(LIB)
CFLAGS += -I$(LIB)/3pp/include
CFLAGS += -Ibuild/cpp/include
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
LDFLAGS += -L$(LIB)/3pp/lib
LIBS += -lpcre2-32
LIBS += -luv
LIBS += -lpthread
LIBS += -ldl
{transpiled_cpp}
{objs}
EXE = build/app
TEST_EXE = build/test

all:
	$(MAKE) -f build/Makefile build/transpile {hpps}
	$(MAKE) -f build/Makefile {all_deps}

test:
	$(MAKE) -f build/Makefile build/transpile {hpps}
	$(MAKE) -f build/Makefile $(TEST_EXE)

build/transpile: {transpile_srcs_paths}
	$(MYS) $(TRANSPILE_DEBUG) transpile {transpile_options} -o build/cpp {transpile_srcs}
	touch $@

{copy_hpp_and_cpp}
$(TEST_EXE): $(OBJ) build/mys.$(OBJ_SUFFIX)
	$(MYS_CXX) $(LDFLAGS) -o $@ $^ $(LIBS)

$(EXE): $(OBJ) build/mys.$(OBJ_SUFFIX)
	$(MYS_CXX) $(LDFLAGS) -o $@ $^ $(LIBS)

%.mys.$(OBJ_SUFFIX): %.mys.cpp $(GCH).gch
	$(MYS_CXX) $(CFLAGS) -include $(GCH) -c $< -o $@

%.cpp.o: %.cpp
	$(MYS_CXX) $(CFLAGS) -c $< -o $@

$(GCH).gch: $(LIB)/mys.hpp
	$(MYS_CXX) $(CFLAGS) -c $< -o $@

build/mys.$(OBJ_SUFFIX): $(LIB)/mys.cpp $(GCH).gch
	$(MYS_CXX) $(CFLAGS) -include $(GCH) -c $< -o $@
