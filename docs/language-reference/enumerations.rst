Enumerations
------------

Enumerations are integers with named values, similar to C.

.. code-block:: mys

   enum Color:
       Red
       Green
       Blue

   enum City(u8):
       Linkoping = 5
       Norrkoping
       Vaxjo = 10

   func main():
       assert Color(0) == Color.Red
       assert i64(Color.Blue) == 2
       assert City(5) == City.Linkoping

       try:
           print(Color(3))
       except ValueError:
           print("value error")
