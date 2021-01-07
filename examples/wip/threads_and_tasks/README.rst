Threads and tasks
=================

- A thread is an OS thread.

  - Use threads for time consuming computations that would block the
    task scheduler from scheduling your other tasks.

  - Use threads if your application needs to utilize more than one CPU
    core.

- Tasks are used to do stuff concurrently (not in parallel) within a
  thread. There is one cooperative task scheduler per thread.

- Threads do not share any data.

- Threads communicate by sending and receiving messages over channels.

- Tasks communicates using queues, events, locks, and probably more.

Build and run the program.

.. code-block:: text

   $ mys run
     Main!
       Echoer started!
       Echoer got 1.5 and 'Hi!'.
         Sleeper started!
         Sleeper done!
       Echoer done!
     Main got 'Hi!'.
