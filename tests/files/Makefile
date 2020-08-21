all:
	$(MAKE) test_re
	$(MAKE) test_struct
	$(MAKE) test_main

test_re:
	python3 -m mypy test_re.py
	g++ -Wall -std=gnu++17 test_re.cpp -o test_re.bin
	./test_re.bin
	python3 test_re.py

test_struct:
	python3 -m mypy test_struct.py
	python3 test_struct.py

test_main:
	python3 -m mypy test_main.py
	g++ -Wall -std=gnu++17 test_main.cpp -o test_main.bin
	./test_main.bin
	python3 test_main.py
