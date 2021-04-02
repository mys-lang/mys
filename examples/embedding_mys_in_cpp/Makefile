MYS ?= env PYTHONPATH=$(CURDIR)/../.. python3 -m mys

INC += -Ibuild/speed/cpp/include
INC += -I../../mys/lib
INC += -I../../mys/lib/3pp/include

SRC += ../../mys/lib/mys.cpp
SRC += main.cpp

OBJ += build/speed/cpp/src/embedding_mys_in_cpp/lib.mys.o
OBJ += build/speed/cpp/src/fiber/lib.mys.o
OBJ += build/speed/cpp/src/random/crypto.mys.o
OBJ += build/speed/cpp/src/random/pseudo.mys.o

LIB += -lpcre2-32
LIB += -luv
LIB += -lpthread
LIB += -ldl

all:
	$(MYS) build
	g++ -std=c++17 $(INC) -L../../mys/lib/3pp/lib $(SRC) $(OBJ) $(LIB)
	./a.out
