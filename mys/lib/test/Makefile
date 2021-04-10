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
	$(CXX) -std=c++17 $^ -o $@

-include $(DEP)

%.o: %.cpp
	$(CXX) -std=c++17 -I.. -MMD -c $< -o $@
