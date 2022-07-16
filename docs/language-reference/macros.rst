Macros
------

.. warning::

   Macros are not yet fully implemented.

- Macro functions and methods bodies compiled into the body of the
  caller function or method.

- Parameters may be evaluated zero or more times.

- Macro functions and methods may not return any value.

- Macro names must be upper case.

.. code-block:: mys

   macro CHECK(cond: bool, message: string):
       if not cond:
           print(message)

   func add(a: i64, b: i64) -> i64:
       print(f"Adding {a} and {b}.")

       return a + b

   class Logger:
       enabled: bool

       macro LOG(self, message: string):
           if self.enabled:
               print(message)

   func main():
       logger = Logger(False)
       number = 5

       CHECK(number == 4, "Not 4.")

       print("Logging with logger disabled.")
       logger.LOG(f"3 + 5 = {add(3, number)}")

       print("Logging with logger enabled.")
       logger.enabled = True
       logger.LOG(f"3 + 5 = {add(3, number)}")

Build and run:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Not 4.
   Logging with logger disabled.
   Logging with logger enabled.
   Adding 3 and 5.
   3 + 5 = 8
