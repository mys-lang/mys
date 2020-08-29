CXX ?= g++
CFLAGS += -I../../mys/lib
CFLAGS += -Wall
CFLAGS += -std=c++17
CFLAGS += -O3
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
CFLAGS += -static
CFLAGS += -Wl,--gc-sections
SRC += ../../mys/lib/mys.cpp

all:
	$(MAKE) test_re
	$(MAKE) test_struct
	$(MAKE) basics
	$(MAKE) hello_world
	$(MAKE) strings
	$(MAKE) loops
	$(MAKE) calc
	$(MAKE) various

test_re:
	$(CXX) $(CFLAGS) $(SRC) test_re.mys.cpp -o test_re.bin
	./test_re.bin

test_struct:

basics:
	$(CXX) $(CFLAGS) $(SRC) basics.mys.cpp -o basics.bin
	./basics.bin 5

hello_world:
	$(CXX) $(CFLAGS) $(SRC) hello_world.mys.cpp -o hello_world.bin
	./hello_world.bin

strings:
	$(CXX) $(CFLAGS) $(SRC) strings.mys.cpp -o strings.bin
	./strings.bin

loops:
	$(CXX) $(CFLAGS) $(SRC) loops.mys.cpp -o loops.bin
	./loops.bin

calc:
	$(CXX) $(CFLAGS) $(SRC) calc.mys.dev.cpp -o calc.bin
	./calc.bin

various:
	$(CXX) $(CFLAGS) $(SRC) various.mys.dev.cpp -o various.bin
	./various.bin
