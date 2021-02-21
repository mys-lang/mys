Traceback
=========

Show tradeback.

.. code-block:: text

   $ mys run -- show
   Traceback (most recent call last):
     File "./src/main.mys", line 13, in main
       do_show()
     File "./src/show.mys", line 7, in do_show
       foo()
     File "./src/show.mys", line 4, in foo
       print(traceback())

Error traceback.

.. code-block:: text

   $ mys run -- error
   Traceback (most recent call last):
     File "./src/main.mys", line 15, in main
       do_error()
     File "./src/error.mys", line 10, in do_error
       foo()
     File "./src/error.mys", line 7, in foo
       raise MyError(message)

   MyError(message="Something went wrong.")

Panic traceback.

.. code-block:: text

   $ mys run -- panic
   Traceback (most recent call last):
     File "./src/main.mys", line 17, in main
       do_panic()
     File "./src/panic.mys", line 6, in do_panic
       foo()
     File "./src/panic.mys", line 3, in foo
       print("hi"[i])

   Panic(message="String index 2 is out of range.")
