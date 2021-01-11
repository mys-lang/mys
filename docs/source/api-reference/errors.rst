Errors
------

All error names ends with ``Error`` to distinguish them from other
classes. All errors must implement the ``Error`` trait.

.. code-block:: text

   +-- GeneralError
   +-- UnreachableError
   +-- NotImplementedError
   +-- KeyError
   +-- ValueError
   +-- FileNotFoundError
   +-- NoneError
   +-- SystemExitError

Functions and methods must declare which errors they may raise.

.. code-block:: python

   @raises(TypeError)
   def foo():
       raise TypeError()

   @raises(GeneralError, TypeError)  # As foo() may raise TypeError.
   def bar(value: i32):
       match value:
           case 1:
               raise GeneralError()
           case 2:
               foo()
           case 3:
               try:
                   raise ValueError()
               except ValueError:
                   pass
