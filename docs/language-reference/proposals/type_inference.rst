Type inference
--------------

- Define generic type local variables without specialization.

  .. code-block:: mys

     def main():
         x = []
         # `x` is a list of something that is resolved later.
         x.append(1)
         # `x` is a list of i64.

  .. code-block:: mys

     def main():
         x = {}
         # `x` is a set or dict of something that is resolved later.
         x[5] = True
         # `x` is a dict of i64 to bool.

  .. code-block:: mys

     def main():
         x = {}
         # `x` is a set or dict of something that is resolved later.
         x.add(5)
         # `x` is a set of i64.

  .. code-block:: mys

     @generic(T)
     class Foo:

         def bar(self) -> T:
             return default(T)

     def main():
         foo = Foo()
         # `foo` is a `Foo` of something that is resolved later.
         foo.bar("hi")
         # `foo` is a `Foo[string]`.

- Define a local variable as ``None``.

  .. code-block:: mys

     def main():
         x = None
         # `x` is something that is resolved later.
         x = "hi"
         # `x` is a string.

- Global variable types cannot be inferred.
