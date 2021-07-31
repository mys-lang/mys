Assertions
----------

Use the ``assert`` keyword to check if given condition is true.

.. code-block:: mys

   assert True
   assert 1 != 5
   assert 1 in [1, 3]
   v = 1
   assert v == 2

The ``AssertionError`` error is raised if the condition is not true.

.. code-block:: text

   AssertionError(message="1 == 2 is not true")

Assertions are always compiled into test and debug binaries, but not
by default into optimized application binaries.
