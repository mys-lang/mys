Build process
-------------

``mys build``, ``mys run`` and ``mys test`` does the following:

#. Use Python's parser to transform the source code to an Abstract
   Syntax Tree (AST).

#. Generate C++ code from the AST.

#. Compile the C++ code with ``g++``.

#. Link the application with ``g++``.

Calling mys from GNU Make recipe
--------------------------------

``mys`` uses ``make`` internally. Always prepend the command with
``+`` to share jobserver.


Mocking
-------

.. code-block:: python

   from random.pseudo import random

   def add(value: f64) -> f64:
       return value + random()

   def test_add():
       random_mock_once(5.3)
       assert add(1.0) == 6.3
