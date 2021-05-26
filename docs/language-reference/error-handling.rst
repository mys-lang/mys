Error handling
--------------

Exceptions
^^^^^^^^^^

There are two kinds of exceptions, errors and signals. Signals are
raised when cancelling a fiber, when receiving OS signals, among other
events that are meant to abort the control flow. Errors are raised for
everything else.

Both errors and signals are catched with a bare ``except``.

Errors
""""""

All error names ends with ``Error`` to distinguish them from other
classes. All errors must implement the ``Error`` trait. Catch all
errors with ``except Error``.

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
| ``IndexError``          | Index out of range.                   |
+-------------------------+---------------------------------------+
| ``KeyError``            | Key not found in dictionary.          |
+-------------------------+---------------------------------------+
| ``NotImplementedError`` | Not implemented.                      |
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

Signals
"""""""

.. warning:: Signals are not yet implemented.

All signal names ends with ``Signal`` to distinguish them from other
classes. All signals must implement the ``Signal`` trait. Catch all
signals with ``except Signal``.

Define your own signals, optionally with members. The average user
never defines signals, only errors.

.. code-block:: python

   class FooSignal(Signal):
       pass

   class BarSignal(Signal):
       code: i64
       message: string

Builtin signals:

+-----------------------------+---------------------------------------------------+
| Name                        | Description                                       |
+=============================+===================================================+
| ``SystemExitSignal``        | Exit the system.                                  |
+-----------------------------+---------------------------------------------------+
| ``UnreachableSignal``       | Unreachable code was executed.                    |
+-----------------------------+---------------------------------------------------+
| ``CancelledSignal``         | A fiber was cancelled.                            |
+-----------------------------+---------------------------------------------------+
| ``InterruptSignal``         | Received SIGINT. Always raised in the main fiber. |
+-----------------------------+---------------------------------------------------+
