GXX ?= g++
CFLAGS += -I../../mys
CFLAGS += -Wall
CFLAGS += -std=c++17

all:
	$(MAKE) test_re
	$(MAKE) test_struct
	$(MAKE) test_main
	$(MAKE) basics

test_re:
	PYTHONPATH=../.. python3 -m mypy test_re.mys
	$(GXX) $(CFLAGS) test_re.mys.cpp -o test_re.bin
	./test_re.bin

test_struct:
	PYTHONPATH=../.. python3 -m mypy test_struct.mys

test_main:
	$(GXX) $(CFLAGS) test_main.mys.cpp -o test_main.bin
	./test_main.bin

basics:
	$(GXX) $(CFLAGS) basics.mys.cpp -o basics.bin
	./basics.bin 5
