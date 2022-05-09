Cache
-----

Cache return value based on input using the ``cache`` decorator.

Example
^^^^^^^

.. code-block:: mys

   @cache
   func format(x: i64, y: bool) -> string:
       print(x, y)

       return f"{x} and {y}"

   func main():
       formatted = format(5, True)
       print("format(5, True): ", formatted)
       formatted = format(5, True)
       print("format(5, True): ", formatted)
       formatted = format(2, False)
       print("format(2, False):", formatted)

The output is:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   5 True
   format(5, True):  5 and True
   format(5, True):  5 and True
   2 False
   format(2, False): 2 and False
