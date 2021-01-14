Function and method overloading
-------------------------------

Functions and methods can be overloaded.

.. warning::

   Overloading is not yet implemented.

Calls the first defined function that matches given parameter and
return value types.

.. code-block:: python

   # func 1
   def neg(v: i16) -> i16:
       return -v

   # func 2
   def neg(v: i8) -> i8:
       return -v

   # func 3
   def neg(v: i8) -> i16:
       return -v

   def main():
       v1 = neg(-5)  # Calls func 1.
       v2 = neg(i8(-5))  # Calls func 2.
       v3: i8 = neg(-5)  # Calls func 2.
       v4: i16 = neg(i8(-5))  # Calls func 3.
       v5: i8 = neg(i16(-5))  # Error. No matching function.
