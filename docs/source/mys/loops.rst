Loops
-----

``while`` and ``for`` loops are available.

``while`` loops run until given condition is false or until
``break``.

``for`` loops can only iterate over ranges, lists, dictionaries,
strings and bytes. All but dictionaries supports combinations of
``enumerate()``, ``slice()``, ``reversed()`` and ``zip()``. Never
modify variables you are iterating over, or the program may crash!

.. code-block:: python

   # While.
   v = 0

   while v < 10:
       if v < 3:
           continue
       elif v == 7:
           break

       v += 1

   # Ranges.
   for v in range(10):
       if v < 3:
           continue
       elif v == 7:
           break

   for i, v in enumerate(range(10, 4, -2)):
       pass

   # Lists.
   for v in [3, 1]:
       pass

   for i, v in enumerate([3, 1]):
       pass

   for v, s in zip([3, 1], ["a", "c"]):
       pass

   for v in slice([3, 1, 4, 2], 1, -1):
       pass

   for v in reversed([3, 1, 4, 2]):
       pass

   # Dictionaries.
   for k, v in {2: 5, 6: 2}:
       pass

   # Strings. 'c' is char.
   for c in "foo":
       pass

   for i, c in enumerate("foo"):
       pass

   # Bytes. 'b' is u8.
   for b in b"\x03\x78":
       pass

   for i, b in enumerate(b"\x03\x78"):
       pass
