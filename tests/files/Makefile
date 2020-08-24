CXX ?= g++
CFLAGS += -I../../mys
CFLAGS += -Wall
CFLAGS += -std=c++17
CFLAGS += -O3

all:
	$(MAKE) test_re
	$(MAKE) test_struct
	$(MAKE) basics
	$(MAKE) hello_world
	$(MAKE) strings

test_re:
	PYTHONPATH=../.. python3 -m mypy test_re.mys
	$(CXX) $(CFLAGS) test_re.mys.cpp -o test_re.bin
	./test_re.bin

test_struct:
	PYTHONPATH=../.. python3 -m mypy test_struct.mys

basics:
	$(CXX) $(CFLAGS) basics.mys.cpp -o basics.bin
	./basics.bin 5

hello_world:
	$(CXX) $(CFLAGS) hello_world.mys.cpp -o hello_world.bin
	./hello_world.bin

strings:
	$(CXX) $(CFLAGS) strings.mys.cpp -o strings.bin
	./strings.bin
