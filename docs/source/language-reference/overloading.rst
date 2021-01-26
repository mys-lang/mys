Overloading
-----------

Functions, methods and class operators can be overloaded.

.. warning::

   Overloading is not yet fully implemented.

All overloaded functions must have a unique set of parameters. The
return type is ignored. The same constraints applies to methods and
class operators.

Here is an example where the function `neg()` is overloaded:

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
       v1 = neg(i26(-5))  # Calls func 1.
       v2 = neg(i8(-5))  # Calls func 2.
       # v3 = neg(-5)  # Error. Ambigious call. Both func 1 and 2 possible.
