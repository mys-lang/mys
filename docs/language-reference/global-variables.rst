Global variables
----------------

- Their types cannot be inferred.

- Their names must be upper case snake case.

- Initialized in import order starting from the first import in
  ``main.mys``. Try to avoid circular dependencies between variables
  as it will result in unexpected behaviour.

Example without circular imports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Given the code below, the global variables are initialized in this
order:

#. ``B = -2`` (from bar.mys)

#. ``Z = 5`` (from bar.mys)

#. ``C = 99`` (from fie.mys)

#. ``Y = 2 * Z`` (from foo.mys)

#. ``A = -1`` (from foo.mys)

#. ``X = Y + 5`` (from main.mys)

The program will print ``X: 15``.

main.mys:

.. code-block:: mys

   from .foo import Y

   X: i64 = Y + 5

   func main():
       print("X:", X)

foo.mys:

.. code-block:: mys

   from .bar import Z
   from .fie import C

   Y: i64 = 2 * Z
   A: i64 = C

bar.mys:

.. code-block:: mys

   B: i64 = -2
   Z: i64 = 5

fie.mys:

.. code-block:: mys

   C: i64 = 99

Example with circular imports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The same files as in the example above, but with circular
imports. ``bar.mys`` imports from ``fie.mys``, and ``fie.mys`` imports
from ``bar.mys``.

Global variables are now initialized in a slightly different
order.

Note that ``B`` in ``C = 99 + B`` is not yet set to ``-2`` as the bar
module is not yet initialized. ``B`` will be ``0`` in this expression,
resulting in ``C = 99``.

#. ``C = 99 + B`` (from fie.mys)

#. ``B = -2`` (from bar.mys)

#. ``Z = 5 + C`` (from bar.mys)

#. ``Y = 2 * Z`` (from foo.mys)

#. ``A = -1`` (from foo.mys)

#. ``X = Y + 5`` (from main.mys)

The program will print ``X: 213``.

main.mys:

.. code-block:: mys

   from .foo import Y

   X: i64 = Y + 5

   func main():
       print(X)

foo.mys:

.. code-block:: mys

   from .bar import Z
   from .fie import C

   Y: i64 = 2 * Z
   A: i64 = C

bar.mys:

.. code-block:: mys

   from .fie import C

   B: i64 = -2
   Z: i64 = 5 + C

fie.mys:

.. code-block:: mys

   from .bar import B

   C: i64 = 99 + B
