Optionals
---------

You use optionals in situations where a value may be absent. An
optional represents two possibilities: Either there is a value, and
you can unwrap the optional to access that value, or there isn’t a
value at all.

Add ``?`` after a type to make it optional.

An example
^^^^^^^^^^

Optional variables and parameters.

.. code-block:: mys

   def foo(a: i64, b: i64? = None) -> i64?:
       # Adds `b` if it has a value, otherwise adds 0.
       a += b orelse 0

       # Optionals can be used as booleans to check if it has a value.
       if b:
           b += 0
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

       # `None` and `a` (type i64) can be returned as optional.
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

Another example
^^^^^^^^^^^^^^^

Optional class members.

.. code-block:: mys

   class Foo:
       a: i64
       b: string?
       c: i64?

       def get(self) -> string:
           return self.b orelse "not set"

       def num(self) -> i64:
           if self.c:
               return self.c * self.a
           else:
               return self.a

   def main():
       foo = Foo(5, None, 10)
       assert foo.get() == "not set"
       assert foo.num() == 50
