Generics
--------

.. code-block:: python

   @generic(T1, T2)
   class Foo:
       a: T1
       b: T2

   # Type alias.
   Bar = Foo[i32, string]

   @generic(T)
   def fie(v: T) -> T:
       return v

   def main():
       print(Foo[bool, u8](True, 100))
       print(Foo("Hello!", 5))
       print(Bar(-5, "Yo"))

       print(fie[u8](2))
       print(fie(1))

.. code-block:: text

   $ mys run
   Foo(a: True, b: 100)
   Foo(a: "Hello!", b: 5)
   Bar(a: -5, b: "Yo")
   2
   1
