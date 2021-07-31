Macros
------

.. warning::

   Macros are not yet implemented.

- Macro functions and methods bodies compiled into the body of the
  caller function or method.

- Parameters have types and may be evaluated zero or more times.

- Macro functions and methods may not return any value.

.. code-block:: mys

   def add(a: i64, b: i64) -> i64:
       print(f"Adding {a} and {b}.")
   
       return a + b
   
   class Logger:
       enabled: bool
   
       @macro
       def LOG(self, message: string):
           if self.enabled:
               print(message)
   
   def main():
       logger = Logger(False)
       number = 5
   
       print("Logging with logger disabled.")
       logger.LOG(f"3 + 5 = {add(3, number)}")
   
       print("Logging with logger enabled.")
       logger.enabled = True
       logger.LOG(f"3 + 5 = {add(3, number)}")

Build and run:

.. code-block:: text

   $ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Logging with logger disabled.
   Logging with logger enabled.
   Adding 3 and 5.
   3 + 5 = 8
