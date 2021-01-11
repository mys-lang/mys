Packages
--------

A package contains modules that other packages can import from. Most
packages contains a file called ``lib.mys``, which is imported from
with ``from <package> import <function/class/variable>``.

Packages that contains ``src/main.mys`` produces executables when
built. Such packages may also be imported from by other packages, in
which case ``src/main.mys`` is ignored.

A package:

.. code-block:: text

   my-package/
   ├── LICENSE
   ├── package.toml
   ├── pylintrc
   ├── README.rst
   └── src/
       ├── lib.mys
       └── main.mys         # Only part of packages that can build executables.

The mys command line interface:

.. code-block:: text

   mys new      Create a new package.
   mys build    Build the appliaction.
   mys run      Build and run the application.
   mys test     Build and run tests.
   mys clean    Remove build output.
   mys lint     Perform static code analysis.
   mys publish  Publish a release.
   mys install  Install an application from local package or registry.

Importing functions, enums, traits, classes and variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

List of packages
^^^^^^^^^^^^^^^^

Some works, some does not even compile. Big work in progress!

- `argparse`_ - Command line argument parser.

- `base64`_ - Base64 encoding and decoding.

- `bits`_ - Basic bits operations.

- `json`_ - JSON encoding and decoding.

- `log`_ - Logging facilities.

- `math`_ - Basic math operations.

- `random`_ - Random numbers.

- `sqlite`_ - SQLite.

- `system`_ - System services.

- `time`_ - Date and time.

.. _argparse: https://github.com/mys-lang/mys-argparse

.. _base64: https://github.com/mys-lang/mys-base64

.. _bits: https://github.com/mys-lang/mys-bits

.. _json: https://github.com/mys-lang/mys-json

.. _log: https://github.com/mys-lang/mys-log

.. _math: https://github.com/mys-lang/mys-math

.. _random: https://github.com/mys-lang/mys-random

.. _sqlite: https://github.com/mys-lang/mys-sqlite

.. _system: https://github.com/mys-lang/mys-system

.. _time: https://github.com/mys-lang/mys-time
