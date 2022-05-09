Type inference
--------------

- Global variable types cannot be inferred.

- Function and method parameters and return types cannot be inferred.

- Generic variable types can be inferred if the variable

  - is returned from a function or method, by iteself or in tuple.

    .. code-block:: mys

       func foo() -> [i64]:
           x = []

           return x

    .. code-block:: mys

       func foo() -> (string, [i64]):
           x = []

           return ("hi", x)

  - is parameter to function or method call.

    .. code-block:: mys

       func foo(v: [i64]):
           pass

       func main():
           x = []
           foo(x)

  - calls a method with a known parameter type.

    .. code-block:: mys

       func foo():
           x = []
           x.append(1)  # 1 is known to be i64

    .. code-block:: mys

       func foo():
           x = []
           y = "hi"
           x.append(y)

- Variables defined to ``None`` can have their types inferred.

    .. code-block:: mys

       func main():
           x = None
           x = "hi"

    .. code-block:: mys

       func main():
           if True:
               x = None
           else:
               x = "hi"
