Optionals
---------

.. warning::

   Optionals are not yet implemented.

You use optionals in situations where a value may be absent. An
optional represents two possibilities: Either there is a value, and
you can unwrap the optional to access that value, or there isn’t a
value at all.

Add ``?`` after a type to make it optional.

.. code-block:: python

   def foo(a: i64, b: i64? = None) -> i64?:
       # Adds `b` if it has a value, otherwise adds 0.
       a += b orelse 0

       # Optional values can be used as booleans to check if it has a
       # value.
       if b:
           a += b

       # Optionals can be matched.
       match b:
           case 1:
               print("Matched one.")
           case 5:
               print("Matched five.")
           case None:
               print("Matched None.")
           case _:
               print(f"Matched {b}.")

       # Clear any value.
       b = None

       # Adding `b` without a value will terminate the application.
       # a += b

       # `None` and `b` (type i64) can be returned as optional.
       if a == 0:
           return None
       else:
           return a

   def main():
       assert foo(1, None) == 1
       assert foo(1, 5) == 11
       b: i64? = 5
       assert foo(1, b) == 11
       assert not foo(0)
       assert foo(0) orelse -1 == -1

       for i in range(5):
           res = foo(i, 0)

           if res:
               print("res has a value")
           else:
               print("res does not have a value")
