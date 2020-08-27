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
	$(MAKE) various

test_re:
	$(CXX) $(CFLAGS) ../../mys/mys.cpp test_re.mys.cpp -o test_re.bin
	./test_re.bin

test_struct:

basics:
	$(CXX) $(CFLAGS) ../../mys/mys.cpp basics.mys.cpp -o basics.bin
	./basics.bin 5

hello_world:
	$(CXX) $(CFLAGS) ../../mys/mys.cpp hello_world.mys.cpp -o hello_world.bin
	./hello_world.bin

strings:
	$(CXX) $(CFLAGS) ../../mys/mys.cpp strings.mys.cpp -o strings.bin
	./strings.bin

loops:
	$(CXX) $(CFLAGS) ../../mys/mys.cpp loops.mys.cpp -o loops.bin
	./loops.bin

calc:
	$(CXX) $(CFLAGS) ../../mys/mys.cpp calc.mys.dev.cpp -o calc.bin
	./calc.bin

various:
	$(CXX) $(CFLAGS) ../../mys/mys.cpp various.mys.dev.cpp -o various.bin
	./various.bin
