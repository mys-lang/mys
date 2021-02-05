The super tiny compiler
=======================

Based on https://github.com/jamiebuilds/the-super-tiny-compiler.

Run with default input code

.. code-block::

   $ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Input:  (add 2 (subtract 4 2))
   Output: add(2, subtract(4, 2));

and with user supplied input code

.. code-block::

   $ mys run -- "(foo 5 \"10\")"
    ✔ Reading package configuration (0 seconds)
    ✔ Building (4.25 seconds)
   Input:  (foo 5 "10")
   Output: foo(5, "10");
