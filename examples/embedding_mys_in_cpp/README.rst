Embedding Mys in C++
====================

A small example of how to embed Mys in C++.

.. code-block::

   $ make
   mys build
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   g++ -std=c++17 -Ibuild/speed/cpp/include -I../../mys/lib -I../../mys/lib/3pp/include -L../../mys/lib/3pp/lib ../../mys/lib/mys.cpp main.cpp build/speed/cpp/src/embedding_mys_in_cpp/lib.mys.o build/speed/cpp/src/fiber/lib.mys.o build/speed/cpp/src/random/crypto.mys.o build/speed/cpp/src/random/pseudo.mys.o -lpcre2-32 -luv
   ./a.out
   Will compute 2 times 3.
   6
   Will compute 3 times -4.
   -12
   0.51787
   0.851855
