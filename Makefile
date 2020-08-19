test:
	python3 setup.py test
	python3 tests/files/main.py
	python3 -m mypy tests/files/main.py
	g++ -Wall -std=gnu++11 tests/files/main.cpp
	./a.out
