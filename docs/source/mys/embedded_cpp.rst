Extending Mys with C++
----------------------

Extending Mys with C++ is extremly easy and flexible. Strings that
starts with ``mys-embedded-c++`` are inserted at the same location in
the generated code.

.. code-block:: python

   def main():
       a: i32 = 0
       b: i32 = 0

       """mys-embedded-c++

       b = 2;
       a++;
       """

       print("a + b:", a + b)
