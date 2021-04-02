Embedding Mys in C++
====================

A small example of how to embed Mys in C++.

.. code-block::

   $ mys build
   $ g++ -Ibuild/speed/cpp/include -Imys/lib \
         build/speed/cpp/src/foo/lib.mys.cpp main.cpp
   $ ./a.out
