Errors
------

All error names ends with ``Error`` to distinguish them from other
classes. All errors must implement the ``Error`` trait.

Define your own errors, optionally with members.

.. code-block:: python

   class FooError(Error):
       pass

   class BarError(Error):
       code: i64
       message: string

Builtin errors:

+-------------------------+---------------------------------------+
| Name                    | Description                           |
+=========================+=======================================+
| ``AssertionError``      | An assertion failed.                  |
+-------------------------+---------------------------------------+
| ``IndexError``          | List index out of range.              |
+-------------------------+---------------------------------------+
| ``KeyError``            | Key not found in dictionary.          |
+-------------------------+---------------------------------------+
| ``NoneError``           | Member access or method call on None. |
+-------------------------+---------------------------------------+
| ``NotImplementedError`` | Not implemented.                      |
+-------------------------+---------------------------------------+
| ``SystemExitError``     | Exit the system.                      |
+-------------------------+---------------------------------------+
| ``UnreachableError``    | Unreachable code was executed.        |
+-------------------------+---------------------------------------+

Functions and methods must declare which errors they may raise. **This
is not yet implemented.**

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
