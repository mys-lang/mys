ifneq ($(shell which ccache),)
CCACHE := ccache
endif

EXE = test
SRC += test_memory.cpp
SRC += catch.cpp
OBJ = $(SRC:%.cpp=%.o)
DEP = $(OBJ:%.o=%.d)

.PNONY: all clean

all: $(EXE)
	./$(EXE) $(ARGS)

clean:
	rm -f $(EXE) $(OBJ) $(DEP)

$(EXE): $(OBJ)
	$(CCACHE) $(CXX) -std=c++17 $^ -o $@

-include $(DEP)

%.o: %.cpp
	$(CCACHE) $(CXX) -std=c++17 -I.. -MMD -c $< -o $@
