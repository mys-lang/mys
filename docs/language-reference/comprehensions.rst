Comprehensions
--------------

.. _list-comprehensions:

List comprehensions
^^^^^^^^^^^^^^^^^^^

List comprehensions provide a concise way to create lists. Common
applications are to make new lists where each element is the result of
some operations applied to each member of another iterable, or to
create a subsequence of those elements that satisfy a certain
condition.

For example, we can create a list of squares, like

.. code-block:: python

   print([x ** 2 for x in [1, 7, 3, 9]])

which is more concise than using a for loop

.. code-block:: python

   squares = []

   for x in [1, 7, 3, 9]:
       squares.append(x)

   print(squares)

The output of both code snippets above is

.. code-block::

   [1, 49, 9, 81]

Use ``if`` to apply a filter, like

.. code-block:: python

   print([x ** 2 for x in [1, 7, 3, 9] if x > 4])

which prints

.. code-block::

   [49, 81]

.. _dict-comprehensions:
   
Dict comprehensions
^^^^^^^^^^^^^^^^^^^

Similar to list comprehensions, but produces a dictionary instead of a
list.

For example, we can create a dictionary of numbers and squares, like

.. code-block:: python

   print({x: x ** 2 for x in [1, 7, 3, 9]})

which prints

.. code-block::

   {1: 1, 7: 49, 3: 9, 9: 81}

Set comprehensions
^^^^^^^^^^^^^^^^^^^

.. warning::

   Set comprehensions are not yet implemented.

Similar to list comprehensions, but produces a set instead of a list.

For example, we can create a set of squares, like

.. code-block:: python

   print({x ** 2 for x in [1, 7, 3, 9]})

which prints

.. code-block::

   {1, 49, 9, 81}
