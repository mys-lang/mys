Enumerations
------------

Enumerations are integers with named values, similar to C.

ToDo: Introduce the enum keyword.

.. code-block:: python

   @enum
   class Color:
       Red
       Green
       Blue

   @enum(u8)
   class City:
       Linkoping = 5
       Norrkoping
       Vaxjo = 10

   def main():
       assert Color(0) == Color.Red

       # Color(3) raises ValueError since 3 is not a color.
