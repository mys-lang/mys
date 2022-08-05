Macros
------

Macro function and method bodies are compiled into the body of the
caller function or method. Macro parameters may be evaluated zero or
more times.

Macro names must be upper case to distinguish them from regular
functions and methods.

Possibly allow modifying the AST in macros in the future.

.. code-block:: mys

   macro CHECK(cond: bool, message: string):
       if not cond:
           print(message)

   func not_four() -> string:
       print("Called not_four().")

       return "Not 4."

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
       number = 4

       CHECK(number == 4, not_four())

       print("Logging with logger disabled.")
       logger.LOG(f"3 + 4 = {add(3, number)}")

       print("Logging with logger enabled.")
       logger.enabled = True
       logger.LOG(f"3 + 4 = {add(3, number)}")

Build and run:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Logging with logger disabled.
   Logging with logger enabled.
   Adding 3 and 4.
   3 + 4 = 7
