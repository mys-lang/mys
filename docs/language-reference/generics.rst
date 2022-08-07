Generics
--------

Generic functions, classes and traits are useful to reuse logic for
multiple types.

Generic types cannot be optionals.

Example code:

.. code-block:: mys

   @generic(T1, T2)
   class Foo:
       a: T1
       b: T2

   @generic(T)
   func fie(v: T) -> T:
       return v

   func main():
       print(Foo[bool, u8](True, 100))
       print(Foo("Hello!", 5))  # Not yet implemented.

       print(fie[u8](2))
       print(fie(1))  # Not yet implemented.

Build and run:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Foo(a: True, b: 100)
   Foo(a: "Hello!", b: 5)
   2
   1
