CXX ?= g++
CFLAGS += -I../../mys/lib
CFLAGS += -Wall
CFLAGS += -Wno-unused-variable
CFLAGS += -std=c++17
CFLAGS += -O3
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
CFLAGS += -static
CFLAGS += -Wl,--gc-sections
SRC += ../../mys/lib/mys.cpp

all:
	# $(MAKE) basics
	$(MAKE) hello_world
	$(MAKE) strings
	$(MAKE) loops
	$(MAKE) calc
	$(MAKE) various

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
	$(CXX) $(CFLAGS) $(SRC) calc.mys.cpp -o calc.bin
	./calc.bin

various:
	$(CXX) $(CFLAGS) $(SRC) various.mys.cpp -o various.bin
	./various.bin
