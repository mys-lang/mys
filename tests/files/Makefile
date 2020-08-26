CXX ?= g++
CFLAGS += -I../../mys
CFLAGS += -Wall
CFLAGS += -std=c++17
CFLAGS += -O3
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
CFLAGS += -static
CFLAGS += -Wl,--gc-sections

all:
	$(MAKE) test_re
	$(MAKE) test_struct
	$(MAKE) basics
	$(MAKE) hello_world
	$(MAKE) strings
	$(MAKE) loops
	$(MAKE) calc

test_re:
	$(CXX) $(CFLAGS) test_re.mys.cpp -o test_re.bin
	./test_re.bin

test_struct:

basics:
	$(CXX) $(CFLAGS) basics.mys.cpp -o basics.bin
	./basics.bin 5

hello_world:
	$(CXX) $(CFLAGS) hello_world.mys.cpp -o hello_world.bin
	./hello_world.bin

strings:
	$(CXX) $(CFLAGS) strings.mys.cpp -o strings.bin
	./strings.bin

loops:
	$(CXX) $(CFLAGS) loops.mys.cpp -o loops.bin
	./loops.bin

calc:
	$(CXX) $(CFLAGS) calc.mys.dev.cpp -o calc.bin
	./calc.bin
