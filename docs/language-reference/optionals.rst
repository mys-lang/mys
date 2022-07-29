Optionals
---------

.. warning::

   Optionals are not yet fully implemented.

You use optionals in situations where a value may be absent. An
optional represents two possibilities: Either there is a value, and
you can unwrap the optional to access that value, or there isn’t a
value at all.

Add ``?`` after a type to make it optional.

It's not allowed to make an optional optional. For example ``i64??``
is invalid.

Examples
^^^^^^^^

Optional variables and parameters
"""""""""""""""""""""""""""""""""

.. code-block:: mys

   func foo(a: i64, b: i64? = None) -> i64?:
       # Compare to `None` to check for value existence.
       if b is not None:
           b += b
           a += b

       # Optionals can be matched.
       match b:
           case None:
               print("Matched None.")
           case 1:
               print("Matched one.")
           case 5:
               print("Matched five.")
           case _:
               print(f"Matched {b}.")

       # Clear any value.
       b = None

       # Adding `b` without a value will panic.
       # a += b

       # `None` and `a` (type i64) can be returned as optional.
       if a == 0:
           return None
       else:
           return a

   func main():
       assert foo(1, None) == 1
       assert foo(1, 5) == 11
       b: i64? = 5
       assert foo(1, b) == 11
       assert foo(0) is None

       for i in range(2):
           res = foo(i, 0)

           if res is not None:
               print("res has a value.")
           else:
               print("res does not have a value.")

.. code-block:: myscon

   Matched 10.
   Matched 10.
   Matched None.
   Matched 0.
   res does not have a value
   Matched 0.
   res has a value

Optional class members
""""""""""""""""""""""

.. code-block:: mys

   class Foo:
       a: i64
       b: string?
       c: i64?

       func get(self) -> string:
           return self.b orelse "not set"

       func num(self) -> i64:
           if self.c is not None:
               return self.c * self.a
           else:
               return self.a

   func main():
       foo = Foo(5, None, 10)
       assert foo.get() == "not set"
       assert foo.num() == 50
