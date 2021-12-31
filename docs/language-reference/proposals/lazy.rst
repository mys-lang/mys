Lazy
----

- Lazy parameters are only evaluated if used.

Example
^^^^^^^

.. code-block:: mys

   def add(a: i64, b: i64) -> i64:
       print(f"Adding {a} and {b}.")

       return a + b

   class Logger:
       enabled: bool

       def log(self, message: lazy[string]):
           if self.enabled:
               print(message)

   def main():
       logger = Logger(False)
       number = 5

       print("Logging with logger disabled.")
       logger.log(f"3 + 5 = {add(3, number)}")

       print("Logging with logger enabled.")
       logger.enabled = True
       logger.log(f"3 + 5 = {add(3, number)}")

The output is:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Logging with logger disabled.
   Logging with logger enabled.
   Adding 3 and 5.
   3 + 5 = 8
