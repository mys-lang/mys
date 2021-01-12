Concurrency
===========

The idea is that an application may have one or more threads (these are
OS threads). Each thread has a cooperative task scheduler. Tasks can
only communicate with other tasks in the same thread. Threads
communicates over channels.

This should eliminate any race conditions that could cause memory
corruption as two threads cannot access the same memory
region. Communication between tasks should be very efficient, but
communication between threads will be more expensive as messages sent
on channels will likely be copied. Also, as there would probably be
one memory allocator per thread no locks are needed, which is a good
thing.

Mostly the same information as above, but as bullets:

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
