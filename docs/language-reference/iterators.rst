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

An iterator method example
^^^^^^^^^^^^^^^^^^^^^^^^^^

``chunks()`` is an iterator method that yields chunks of ``size``
bytes.

.. code-block:: python

   class Memory:
       data: bytes

       @iterator
       def chunks(self, size: u64) -> bytes:
           for offset in range(0, i64(len(data)), i64(size)):
               yield self.data[offset:offset + size]

   def main():
       for chunk in Memory(b"123456789").chunks(4):
           print(chunk)

The output is:

.. code-block:: text

   $ mys run
   b"\x31\x32\x33\x34"
   b"\x35\x36\x37\x38"
   b"\x39"

Implementation ideas
^^^^^^^^^^^^^^^^^^^^

Somehow convert iterator functions and methods to a class with a state
machine.

.. code-block:: python

   # def fibonaccis(count: int) -> (int, int):
   #     curr = 0
   #     next = 1
   #     i = 0
   #
   #     while i < count:
   #         yield (i, curr)
   #         yield (i, curr)
   #         temp = curr
   #         curr = next
   #         next += temp
   #         i += 1

   class Fibonaccis:

       def __init__(self, count: int):
           self._curr = None
           self._next = None
           self._i = None
           self._count = count
           self._state = 0

       def next(self) -> (int, int):
           while True:
               if self._state == 0:
                   self._curr = 0
                   self._next = 1
                   self._i = 0
                   self._state = 1
               elif self._state == 1:
                   if self._i < self._count:
                       self._state = 2

                       return (self._i, self._curr)
                   else:
                       self._state = 4
               elif self._state == 2:
                   self._state = 3

                   return (self._i, self._curr)
               elif self._state == 3:
                   temp = self._curr
                   self._curr = self._next
                   self._next += temp
                   self._i += 1
                   self._state = 1
               elif self._state == 4:
                   raise RuntimeError()

   def main():
       fibonaccis = Fibonaccis(10)

       while True:
           try:
               index, number = fibonaccis.next()
           except RuntimeError:
               break

           print(f"fibonacci({index}): {number}")

   main()
