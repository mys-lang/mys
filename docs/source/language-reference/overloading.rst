Function and method overloading
-------------------------------

Functions and methods can be overloaded.

.. warning::

   Overloading is not yet implemented.

All overloaded functions must have a unique set of parameters. The
return type is ignored.

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
       v1 = neg(-5)  # Calls func 1.
       v2 = neg(i8(-5))  # Calls func 2.
       # v3: i8 = neg(-5)  # Error. Return value mismatch. Func 1
                           # returns i16, not i8.
