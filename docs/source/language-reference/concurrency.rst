Concurrency
-----------

.. warning::

   Concurrency is not yet fully implemented.

Concurrency is implemented with stackful fibers scheduled by a
cooperative (not preemptive) scheduler. Only one fiber can run at a
time, which essentially makes Mys single core. Multi core support may
be added in the future if requested.

Fibers and asynchronous IO is currently implemented using pthreads and
`libuv`_.

See `the fibers example`_ for example code.

Scheduler
^^^^^^^^^

There are two fibers that are always present; the main fiber and the
idle fiber. The main fiber calls the application entry point
``main()``. The idle fiber is running when no other fiber is ready to
run. It waits for IO events to occur and then reschedules to run other
ready fibers.

The diagram below is an example of how three fibers; ``shell``,
``main`` and ``idle`` are scheduled over time.

.. image:: ../_static/concurrency-scheduling.png

As it is a single core scheduler only one fiber is running at a
time. In the beginning the system is idle and the ``idle`` fiber is
running. After a while the ``main`` and ``shell`` fibers have some
work to do, and since they have higher priority than the ``idle``
fiber they are scheduled. At the end the ``idle`` fiber is running
again.

.. _the fibers example: https://github.com/mys-lang/mys/tree/main/examples/fibers/src/main.mys

.. _libuv: https://libuv.org/
