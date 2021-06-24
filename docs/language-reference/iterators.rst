Iterators
---------

.. warning::

   Iterators are not yet implemented.

Use ``for``-loops to iterate over iterators. Iterators cannot be
stored in variables or passed to functions or methods (maybe support
this later with ``next()``-method). They must be immediately consumed
in a ``for``-loop.

Use the ``@iterator`` decorator to make a function or method an
iterator.

Use the ``yield`` keyword to yield items from the iterator.

Fibonacci example
^^^^^^^^^^^^^^^^^

``fibonaccis()`` is an iterator function that yields ``count`` number
of fibonacci numbers.

.. code-block:: python

   @iterator
   def fibonaccis(count: i64) -> (i64, i64):
       curr = 0
       next = 1

       for i in range(count):
           yield (i, curr)

           temp = curr
           curr = next
           next += temp

   def main():
       for index, number in fibonaccis(10):
           print(f"fibonacci({index}): {number}")

The output is:

.. code-block:: text

   $ mys run
   fibonacci(0): 0
   fibonacci(1): 1
   fibonacci(2): 1
   fibonacci(3): 2
   fibonacci(4): 3
   fibonacci(5): 5
   fibonacci(6): 8
   fibonacci(7): 13
   fibonacci(8): 21
   fibonacci(9): 34
