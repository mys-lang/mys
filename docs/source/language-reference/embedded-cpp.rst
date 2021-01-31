Extending Mys with C++
----------------------

.. warning::

   The Mys C++ API may change at any time and should be avoided if
   possible.

Extending Mys with C++ is extremly easy and flexible. Strings that
starts with ``mys-embedded-c++`` are inserted at the same location in
the generated code. Also, all ``.cpp`` files found in ``src/`` are
compiled and linked with the application.

Using C and C++ libraries is not yet supported.

Below is the contents of ``src/main.mys`` found in the `embedded_cpp
example`_.

.. code-block:: python

   """mys-embedded-c++-before-namespace
   #include "cpp/foo.hpp"
   """

   def main():
       a: i32 = 0
       b: i32 = 0

       c"""
       b = foo::foobar(2);
       a++;
       """

       print("a + b:", a + b)

.. _embedded_cpp example: https://github.com/mys-lang/mys/tree/main/examples/embedded_cpp
