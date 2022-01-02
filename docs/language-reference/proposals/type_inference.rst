Type inference
--------------

- Define generic type local variables without specialization.

  .. code-block:: mys

     def main():
         x = []
         # `x` is a list of something that is resolved later.
         x.append(1)
         # `x` is a list of i64.

- Define a local variable as ``None``.

  .. code-block:: mys

     def main():
         x = None
         # `x` is something that is resolved later.
         x = "hi"
         # `x` is a string.

- Global variable types cannot be inferred.
