Traceback
=========

Print a traceback and let the application exit normally.

.. code-block:: text

   $ mys run -o debug -- print
   Traceback (most recent call last):
     File "./src/main.mys", line 13, in main
       do_print()
     File "./src/print.mys", line 7, in do_print
       foo()
     File "./src/print.mys", line 4, in foo
       print(traceback())

Raise an error that is not caught. The Mys runtime prints a traceback
and the error.

.. code-block:: text

   $ mys run -o debug -- error
   Traceback (most recent call last):
     File "./src/main.mys", line 15, in main
       do_error()
     File "./src/error.mys", line 10, in do_error
       foo()
     File "./src/error.mys", line 7, in foo
       raise MyError(message)

   MyError(message="Something went wrong.")

Panics prints a traceback and a message.

.. code-block:: text

   $ mys run -o debug -- panic
   h
   i
   Traceback (most recent call last):
     File "./src/main.mys", line 17, in main
       do_panic()
     File "./src/panic.mys", line 6, in do_panic
       foo()
     File "./src/panic.mys", line 3, in foo
       print("hi"[i])

   Panic(message="String index 2 is out of range.")
