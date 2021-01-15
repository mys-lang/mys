Global variables
----------------

Their types can't be inferred (for now).

Their names must be upper case snake case.

Initialized in import order starting from the first import in
``main.mys``. Circular dependencies between variables during
initialization is not allowed.

.. warning::

   Initialization order is not yet implemented.

Given the code below, the global variables are initialized in this
order:

#. ``B = -2`` (from bar.mys)

#. ``Z = 5`` (from bar.mys)

#. ``C = 99`` (from fie.mys)

#. ``Y = 2 * Z`` (from foo.mys)

#. ``A = -1`` (from foo.mys)

#. ``X = Y + 5`` (from main.mys)

main.mys:

.. code-block:: python

   from .foo import Y

   X: i32 = Y + 5

   def main():
       print(X)

foo.mys:

.. code-block:: python

   from .bar import Z
   from .fie import C

   Y: i32 = 2 * Z
   A: i32 = C

bar.mys:

.. code-block:: python

   B: i32 = -2
   Z: i32 = 5

fie.mys:

.. code-block:: python

   C: i32 = 99
