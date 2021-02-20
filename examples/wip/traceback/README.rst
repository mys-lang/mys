Traceback
=========

Panic traceback.

.. code-block:: text

   $ mys run -- panic
   Traceback (most recent call last):
     File "./src/main.mys", line 12, in main
       do_panic()
     File "./src/panic.mys", line 6, in do_panic
       foo()
     File "./src/panic.mys", line 3, in foo
       print("hi"[i])

   Panic(message="String index 2 is out of range.")

Error traceback.

.. code-block:: text

   $ mys run -- error
   Traceback (most recent call last):
     File "./src/main.mys", line 14, in main
       do_error()
     File "./src/error.mys", line 10, in do_error
       foo()
     File "./src/error.mys", line 7, in foo
       raise MyError(message)

   MyError(message="Something went wrong.")
