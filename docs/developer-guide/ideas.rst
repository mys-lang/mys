Ideas
-----

Various ideas.

Mocking
^^^^^^^

.. code-block:: python

   from random.pseudo import random

   def add(value: f64) -> f64:
       return value + random()

   def test_add():
       random_mock_once(5.3)
       assert add(1.0) == 6.3
