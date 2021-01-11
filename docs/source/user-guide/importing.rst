Importing
^^^^^^^^^

Import functions, enums, traits, classes and variables from modules in
other packages with ``from <module> import <name>``.

Import functions, enums, traits, classes and variables from modules in
current package with ``from .<module> import <name>``. One ``.`` per
directory level.

Use ``from <module> import <name> as <new-name>`` to use a custom name.

- Imports are private. They cannot be exported.

- Circular imports are allowed.

- A module is private if its name or any directory in its path starts
  with an underscore.

- A private module can only be imported from by other modules in the
  same package.

- All public definitions in a private module can only be used by other
  modules in the same package.

- Imports from modules within the same package must be relative.

Here are a few examples:

.. code-block:: python

   from mypkg1 import func1                   # Imports from mypkg1/src/lib.mys.
   from mypkg2.subpkg1.mod1 import func2 as func3
   from mypkg2 import Class1
   from mypkg2 import var1
   from ..mod1 import func4                   # Imports from ../mod1.mys.
   from ...subpkg2.mod1 import func5          # Imports from ../../subpkg2/mod1.mys.
   from . import func6                        # Imports from lib.mys in the same
                                              # folder.
   # from mypkg2._mod1 import func7           # Not allowed as _mod1 is private.
   # from mypkg2._subpkg1.mod1 import func8   # Not allowed as _subpkg1 and all its
                                              # content is private.
   from ._mod1 import func7                   # Imports from private _mod1.mys.
   from ._subpkg1.mod1 import func8           # Imports from private _subpkg1/mod1.mys.

   def foo():
       func1()
       func3()
       Class1()
       print(var1)
       func4()
       func5()
       func6()
