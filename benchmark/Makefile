SHELL = /bin/bash

all:
	time python3 main.py
	g++ -Wall -O2 -std=gnu++17 -Iboost_1_73_0 main.mys.cpp
	time ./a.out
