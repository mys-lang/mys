Message passing
===============

Two threads, student and calculator, communicating by sending
messages.

Add() and Result() are messages.

.. code-block:: text

         +------------+                     +------------+
         |   student  |                     | calculator |
         +------------+                     +------------+
                |                                 |
      timeout   |                                 |
    ----------->|                                 |
                |   Add(first=0.2, second=0.11)   |
                |-------------------------------->|
                |        Result(value=0.31)       |
                |<--------------------------------|
                .                                 .
                .                                 .
      timeout   |                                 |
    ----------->|                                 |
                |   Add(first=1.0, second=0.88)   |
                |-------------------------------->|
                |        Result(value=1.88)       |
                |<--------------------------------|
                .                                 .
                .                                 .

Build and run the program.

.. code-block:: text

   $ mys run
   Press any key to exit.

   Timeout.
   Add(first=1, second=2)
   Result(value=3)

   Timeout.
   Add(first=1, second=2)
   Result(value=3)
   <Enter>
   Calculator stopped.
   Done!
