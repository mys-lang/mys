ifneq ($(shell which ccache),)
CCACHE := ccache
endif

EXE = test
SRC += test_memory.cpp
SRC += catch.cpp
SRC += ../memory.cpp
OBJ = $(SRC:%.cpp=%.o)
DEP = $(OBJ:%.o=%.d)
CXXFLAGS += -DMYS_MEMORY_STATISTICS
CXXFLAGS += -std=c++17
CXXFLAGS += -I..
CXXFLAGS += -MMD

.PNONY: all clean

all: $(EXE)
	./$(EXE) $(ARGS)

clean:
	rm -f $(EXE) $(OBJ) $(DEP)

$(EXE): $(OBJ)
	$(CCACHE) $(CXX) -std=c++17 $^ -o $@

-include $(DEP)

%.o: %.cpp
	$(CCACHE) $(CXX) $(CXXFLAGS) -c $< -o $@
