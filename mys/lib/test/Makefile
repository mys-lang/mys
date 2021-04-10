EXE = test
SRC += test_memory.cpp
SRC += catch.cpp
OBJ = $(SRC:%.cpp=%.o)
DEP = $(OBJ:%.o=%.d)

.PNONY: all clean

all: $(EXE)
	./$(EXE)

clean:
	rm -f $(EXE) $(OBJ) $(DEP)

$(EXE): $(OBJ)
	ccache g++ -std=c++17 $^ -o $@

-include $(DEP)

%.o: %.cpp
	ccache g++ -std=c++17 -I../3pp/include -I.. -MMD -c $< -o $@
