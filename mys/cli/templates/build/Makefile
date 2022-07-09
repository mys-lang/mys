.PHONY: all test pcre2 uv

MYS_DIR = {mys_dir}
LIB = $(MYS_DIR)/lib
#export CCACHE_BASEDIR = $(MYS_DIR)
export CCACHE_SLOPPINESS = pch_defines,time_macros,include_file_mtime,include_file_ctime

STATUS_PATH ?= {status_path}
BUILD := {build}
BUILD_ABS = $(abspath $(BUILD))
GCH := $(BUILD)/mys_pre_
MYS_CXX ?= {ccache}$(CXX)
MYS ?= {mys}
CFLAGS += -I$(BUILD_ABS)/pcre2/include
CFLAGS += -I$(BUILD_ABS)/uv/include
CFLAGS += $(CFLAGS_EXTRA)
CFLAGS += -I$(LIB)
CFLAGS += -I$(BUILD)/cpp/include
CFLAGS += {cflags}
# CFLAGS += -Wall
CFLAGS += -Wno-unused-variable
CFLAGS += -Wno-unused-value
CFLAGS += -Wno-return-type
# CFLAGS += -Wno-parentheses-equality
# CFLAGS += -Wno-unused-but-set-variable
CFLAGS += -Winvalid-pch
CFLAGS += -O{optimize}
CFLAGS += -std=gnu++2a
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
CFLAGS += -fdiagnostics-color=always
# CFLAGS += -flto
ifeq ($(COVERAGE), yes)
CFLAGS += -DMYS_COVERAGE
TRANSPILE_COVERAGE = --coverage
endif
ifeq ($(UNSAFE), yes)
CFLAGS += -DMYS_UNSAFE
endif
ifeq ($(TRACEBACK), yes)
CFLAGS += -DMYS_TRACEBACK
endif
ifeq ($(SANITIZE), yes)
CFLAGS += -fsanitize=address
LDFLAGS += -fsanitize=address
CFLAGS += -fsanitize=undefined
LDFLAGS += -fsanitize=undefined
endif
ifeq ($(TEST), yes)
CFLAGS += -DMYS_TEST
OBJ_SUFFIX = test.o
GCH := $(GCH)test.hpp
EXE = $(BUILD)/test
else
ifeq ($(APPLICATION), yes)
CFLAGS += -DMYS_APPLICATION
GCH := $(GCH)app.hpp
else
GCH := $(GCH).hpp
endif
OBJ_SUFFIX = o
EXE = $(BUILD)/app
endif
LDFLAGS += $(LDFLAGS_EXTRA)
LDFLAGS += -L$(BUILD)/pcre2
LDFLAGS += -L$(BUILD)/uv
LDFLAGS += -std=c++17
# LDFLAGS += -static
LDFLAGS += -fdiagnostics-color=always
# LDFLAGS += -flto
feature = $(shell $(CXX) -Werror $(1) $(BUILD)/feature.cpp 2> /dev/null && echo $(1))
comma := ,
ifeq ({system}, Darwin)
LDFLAGS += $(call feature,-Wl$(comma)-dead_strip)
endif
LDFLAGS += $(call feature,-Wl$(comma)--gc-sections)
LIBS += -lpcre2
LIBS += -luv
LIBS += -lpthread
LIBS += -ldl
LIBS += {libs}
{transpiled_cpp}
{objs}

all: pcre2 uv
	$(MAKE) -f $(BUILD)/Makefile $(BUILD)/transpile {hpps}
	$(MAKE) -f $(BUILD)/Makefile $(BUILD)/transpile {hpps}
	$(MAKE) -f $(BUILD)/Makefile {all_deps} {assets}

test: pcre2 uv
	$(MAKE) -f $(BUILD)/Makefile $(BUILD)/transpile {hpps}
	$(MAKE) -f $(BUILD)/Makefile $(EXE) {assets}

pcre2:
	rsync -tr $(MYS_DIR)/pcre2 $(BUILD)
	env CC="{ccache}$(CC)" $(MAKE) -C $(BUILD)/pcre2

uv:
	rsync -tr $(MYS_DIR)/uv $(BUILD)
	env CC="{ccache}$(CC)" $(MAKE) -C $(BUILD)/uv SYSTEM={system}

$(BUILD)/transpile: {transpile_srcs_paths}
	@echo "> Transpiling {number_of_modules} modules" >> $(STATUS_PATH)
	$(MYS) $(TRANSPILE_DEBUG) transpile $(TRANSPILE_COVERAGE) \
	{transpile_options} -o $(BUILD)/cpp {transpile_srcs}
	touch $@
	@echo "< Transpiling {number_of_modules} modules" >> $(STATUS_PATH)

{copy_assets}
{copy_hpp_and_cpp}
$(EXE): $(OBJ) $(BUILD)/mys.$(OBJ_SUFFIX)
	@echo "> Linking $@" >> $(STATUS_PATH)
	$(MYS_CXX) $(LDFLAGS) -o $@ $^ $(LIBS)
	@echo "< Linking $@" >> $(STATUS_PATH)

%.mys.$(OBJ_SUFFIX): %.mys.cpp $(GCH).gch
	@echo "> Compiling $<" >> $(STATUS_PATH)
	$(MYS_CXX) $(CFLAGS) -include $(GCH) -c $< -o $@
	@echo "< Compiling $<" >> $(STATUS_PATH)

%.cpp.o: %.cpp
	@echo "> Compiling $<" >> $(STATUS_PATH)
	$(MYS_CXX) $(CFLAGS) -c $< -o $@
	@echo "< Compiling $<" >> $(STATUS_PATH)

$(GCH).gch: $(LIB)/mys.hpp
	@echo "> Compiling $<" >> $(STATUS_PATH)
	$(MYS_CXX) $(CFLAGS) -c $< -MMD -o $@
	@echo "< Compiling $<" >> $(STATUS_PATH)

$(BUILD)/mys.$(OBJ_SUFFIX): $(LIB)/mys.cpp $(GCH).gch
	@echo "> Compiling $<" >> $(STATUS_PATH)
	$(MYS_CXX) $(CFLAGS) -include $(GCH) -c $< -o $@
	@echo "< Compiling $<" >> $(STATUS_PATH)

-include $(GCH).d
