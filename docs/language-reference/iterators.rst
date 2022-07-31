Iterators
---------

.. warning::

   Iterators are not yet fully implemented (not even close).

Use ``for`` loops to iterate over iterators, or call their ``next()``
method to get the next item.

Use ``iterator`` instead of ``func`` to make a function or method an
iterator.

Use ``yield`` to yield items from the iterator. ``return`` is not
allowed in iterators.

Call ``iter()`` to create an iterator from classes that implements
``__iter__()``. ``for``-loops does this automatically.

Iterators implements the builtin generic trait ``Iterator[T]``, where
``T`` is the type of the items produced by the iterator.

The builtin generic iterator trait looks like this:

.. code-block:: mys

   @generic(T)
   trait Iterator:

       func next(self) -> T?
           pass

Fibonacci example
^^^^^^^^^^^^^^^^^

``fibonaccis()`` is an iterator that yields ``count`` number of
fibonacci numbers.

.. code-block:: mys

   iterator fibonaccis(count: i64) -> (i64, i64):
       curr = 0
       next = 1

       for i in range(count):
           yield (i, curr)

           temp = curr
           curr = next
           next += temp

   func main():
       for index, number in fibonaccis(10):
           print(f"fibonacci({index}): {number}")

The output is:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
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

       iterator chunks(self, size: i64) -> bytes:
           for offset in range(0, data.length(), size):
               yield self.data[offset:offset + size]

       iterator __iter__(self) -> u8:
           for value in self.data:
               yield value

   func main():
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
       print(it.next())

The output is:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
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
   None

Iterator type example
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: mys

   func call(numbers: Iterator[string]):
       print("Calling:")

       for number in numbers:
           print(number)

   func main():
       numbers = ["0702293884", "0769912312", "0709957734"]
       call(numbers)
       call(iter(numbers))
       it = iter(numbers)
       it.next()
       call(it)

The output is:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Calling:
   0702293884
   0769912312
   0709957734
   Calling:
   0702293884
   0769912312
   0709957734
   Calling:
   0769912312
   0709957734

Explicitly implementing the iterator trait
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: mys

   class MyIterator(Iterator[i64]):
       _a: i64
       _b: i64
       _c: i64
       _next_letter: char

       func __init__(self):
           self._a = 5
           self._b = 3
           self._c = 1
           self._next_letter = 'a'

       func next(self) -> i64?:
           match self._next_letter:
               case 'a':
                   self._next_letter = 'b'

                   return self._a
               case 'b':
                   self._next_letter = 'c'

                   return self._b
               case 'c':
                   self._next_letter = ''

                   return self._c
               case _:
                   return None

   func main():
       for item in MyIterator():
           print(item)

The output is:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   5
   3
   1
