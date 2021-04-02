INC += -Ibuild/speed/cpp/include
INC += -I../../mys/lib
INC += -I../../mys/lib/3pp/include

SRC += ../../mys/lib/mys.cpp
SRC += main.cpp

OBJ += build/speed/cpp/src/embedding_mys_in_cpp/lib.mys.o
OBJ += build/speed/cpp/src/fiber/lib.mys.o
OBJ += build/speed/cpp/src/random/crypto.mys.o
OBJ += build/speed/cpp/src/random/pseudo.mys.o

all:
	mys build
	g++ -std=c++17 $(INC) -L../../mys/lib/3pp/lib \
	    $(SRC) $(OBJ) -lpcre2-32 -luv
	./a.out
