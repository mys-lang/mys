Generics
--------

Generic function and classes are useful to reuse logic for multiple
types.

Example code:

.. code-block:: python

   @generic(T1, T2)
   class Foo:
       a: T1
       b: T2

   @generic(T)
   def fie(v: T) -> T:
       return v

   def main():
       print(Foo[bool, u8](True, 100))
       print(Foo("Hello!", 5))  # Not yet implemented.

       print(fie[u8](2))
       print(fie(1))  # Not yet implemented.

Build and run:

.. code-block:: text

   $ mys run
   Foo(a: True, b: 100)
   Foo(a: "Hello!", b: 5)
   2
   1

Ideas
^^^^^

Compiler details. Create one module per generic with selected types.

.. code-block:: python

   from x import Yy
   from m import _Nn
   # Imports from generic module.

   class Foo:
       a: Yy
       b: _Nn
