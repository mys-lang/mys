Iterators
---------

.. warning::

   Iterators are not yet implemented.

Use ``for``-loops to iterate over iterators, or call their
``next()``-method to get the next item.

Use the ``@iterator`` decorator to make a function or method an
iterator.

Use the ``yield`` keyword to yield items from the iterator. ``return``
is not allowed in iterators.

Fibonacci example
^^^^^^^^^^^^^^^^^

``fibonaccis()`` is an iterator function that yields ``count`` number
of fibonacci numbers.

.. code-block:: mys

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

.. code-block:: mys

   class Memory:
       data: bytes

       @iterator
       def chunks(self, size: u64) -> bytes:
           for offset in range(0, i64(len(data)), i64(size)):
               yield self.data[offset:offset + size]

       @iterator
       def __iter__(self) -> u8:
           for value in self.data:
               yield value

   def main():
       print("Chunks:")

       for chunk in Memory(b"123456789").chunks(4):
           print(chunk)

       print()
       print("Default iterator:")

       for byte in Memory(b"0123"):
           print(byte)

       print()
       print("Next method:")

       it = iter(Memory(b"0123"))
       print(it.next())
       print(it.next())
       print(it.next())
       print(it.next())
       print(it.next())

The output is:

.. code-block:: text

   $ mys run
   Chunks:
   b"\x31\x32\x33\x34"
   b"\x35\x36\x37\x38"
   b"\x39"

   Default iterator:
   0
   1
   2
   3

   Next method:
   0
   1
   2
   3
   None
