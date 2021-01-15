Comprehensions
--------------

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

which is more concise than using the regular for loop as seen below.

.. code-block:: python

   squares = []

   for x in [1, 7, 3, 9]:
       squares.append(x)

   print(squares)

The output of both code snippets above is:

.. code-block::

   [1, 49, 9, 81]

Use `if` to apply a filter, like

.. code-block:: python

   print([x ** 2 for x in [1, 7, 3, 9] if x > 4])

which prints

.. code-block::

   [49, 81]

Dict comprehensions
^^^^^^^^^^^^^^^^^^^

Set comprehensions
^^^^^^^^^^^^^^^^^^^
