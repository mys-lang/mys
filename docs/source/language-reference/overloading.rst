Overloading
-----------

Functions, methods and class operators can be overloaded.

.. warning::

   Overloading is not yet fully implemented.

All overloaded functions must have a unique set of parameters. The
return type is ignored. The same constraints applies to methods and
class operators.

Here is an example where the function ``neg()`` is overloaded:

.. code-block:: python

   # func 1
   def neg(v: i16) -> i16:
       return -v

   # func 2
   def neg(v: i8) -> i8:
       return -v

   # func 3, not allowed, same parameters as func 2
   # def neg(v: i8) -> i16:
   #     return -v

   def main():
       v1 = neg(i16(-5))  # Calls func 1.
       v2 = neg(i8(-5))  # Calls func 2.
       # v3 = neg(-5)  # Error. Ambigious call. Both func 1 and 2 possible.

Operator overloading is similar to Python. Below is an example class
that defines ``+``, ``-``, ``*`` and ``/``.

.. code-block:: python

   class Foo:
       v: i64

       def __add__(self, other: Foo) -> Foo:
           return Foo(self.v + other.v)

       def __sub__(self, other: i64) -> Foo:
           return Foo(self.v - other)

       def __mul__(self, other: i64) -> i64:
           return self.v * other

       def __div__(self, other: f64) -> f64:
           return f64(self.v) / other

   def main():
       foo = Foo(5)
       print(foo + Foo(2))
       print(foo - 4)
       print(foo * 2)
       print(foo / 1.5)

Operators to methods mapping table.

+----------+-------------+
| Operator | Method      |
+==========+=============+
| ``+``    | ``__add__`` |
+----------+-------------+
| ``-``    | ``__sub__`` |
+----------+-------------+
| ``*``    | ``__mul__`` |
+----------+-------------+
| ``/``    | ``__div__`` |
+----------+-------------+
