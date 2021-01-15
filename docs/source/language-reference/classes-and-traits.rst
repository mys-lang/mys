Classes and traits
------------------

- Instance members are accessed with ``<object>.<variable/method>``.

- Implemented trait methods may be decorated with ``@trait(T)``.

- Automatically added methods (``__init__()``, ``__str__()``, ...)
  are only added if missing.

- Decorate with ``@trait`` to make a class a trait.

  ToDo: Introduce the trait keyword.

- There is no traditional OOP inheritance. Traits are used instead.

- Traits does not have a state and cannot be instantiated.

Below is a class with a data member ``value`` and a method
``inc()``.

The constructor ``def __init__(self, value: i32 = 0)`` (and more
methods) are automatically added to the class as they are missing.

.. code-block:: python

   class Foo:
       value: i32

       def inc(self):
           self.value += 1

   def main():
       print("f1:")
       f1 = Foo(0)
       print(f1)
       f1.inc()
       print(f1)

       print("f2:")
       f2 = Foo(5)
       print(f2)

.. code-block:: text

   $ mys run
   f1:
   Foo(value=0)
   Foo(value=1)
   f2:
   Foo(value=5)
