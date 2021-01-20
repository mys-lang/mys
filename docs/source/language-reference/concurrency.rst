Concurrency
-----------

.. warning::

   Concurrency is not yet implemented.

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

`C++ coroutines`_ and `libuv`_ should probably be used to implement
tasks (with networking, file access, etc.). There are several
libraries available that tries to implement this combination, for
example `asyncio`_ and `awaituv`_. Implementing threads is not
currently planned.

`Boost fibers`_ is an alternative to `C++ coroutines`_.

See `the concurrency example`_ for example code (that do not
work).

.. _the concurrency example: https://github.com/mys-lang/mys/tree/main/examples/wip/concurrency

.. _C++ coroutines: https://en.cppreference.com/w/cpp/language/coroutines

.. _libuv: https://libuv.org/

.. _awaituv: https://github.com/jimspr/awaituv

.. _asyncio: https://github.com/zhanglix/asyncio

.. _Boost fibers: https://www.boost.org/doc/libs/1_75_0/libs/fiber/doc/html/index.html

.. _Rust segmented stacks: https://without.boats/blog/futures-and-segmented-stacks/
