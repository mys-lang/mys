Type inference
--------------

Generic variable types can be inferred if the variable

- is returned from a function or method, by iteself or in tuple.

  .. code-block:: mys

     def foo() -> [i64]:
         x = []

         return x

  .. code-block:: mys

     def foo() -> (string, [i64]):
         x = []

         return ("hi", x)

- is parameter to function or method call.

  .. code-block:: mys

     def foo(v: [i64]):
         pass

     def main():
         x = []
         foo(x)

- calls a method with a known parameter type.

  .. code-block:: mys

     def foo():
         x = []
         x.append(1)  # 1 is known to be i64

Variables defined to ``None`` can have their types inferred.

  .. code-block:: mys

     def main():
         x = None
         x = "hi"

  .. code-block:: mys

     def main():
         if True:
             x = None
         else:
             x = "hi"

Global variable types cannot be inferred.
