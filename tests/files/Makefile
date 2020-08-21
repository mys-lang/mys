GXX ?= g++

all:
	$(MAKE) test_re
	$(MAKE) test_struct
	$(MAKE) test_main

test_re:
	PYTHONPATH=../.. python3 -m mypy test_re.py
	$(GXX) -Wall -std=gnu++17 test_re.cpp -o test_re.bin
	./test_re.bin
	PYTHONPATH=../.. python3 -c "from test_re import main ; main()"

test_struct:
	PYTHONPATH=../.. python3 -m mypy test_struct.py
	PYTHONPATH=../.. python3 -c "from test_struct import main ; main()"

test_main:
	$(GXX) -Wall -std=gnu++17 test_main.cpp -o test_main.bin
	./test_main.bin
	PYTHONPATH=../.. python3 -c "from test_main import main ; main()"
