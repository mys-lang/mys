Modules and packages
--------------------

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
