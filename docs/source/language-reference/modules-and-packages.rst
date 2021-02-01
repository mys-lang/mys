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

Package configuration
^^^^^^^^^^^^^^^^^^^^^

The package configuarion file is always called ``package.toml`` and
contains various information about the package.

Here is an example:

.. code-block:: toml

   [package]
   name = "sqlite"
   version = "1.6.0"
   authors = ["Erik Moqvist <mys.lang@example.com>"]
   description = "SQLite wrapper."

   [dependencies]
   os = "*"

   [c-dependencies]
   sqlite3 = "*"

- The ``package`` section contains various general information about
  the package.

  - ``name`` is its name.

  - ``version`` is its semantic version.

  - ``authors`` is a list of all authors.

  - ``description`` is a short description.

- The ``dependencies`` sections lists all packages this package
  depends on.

- The ``c-dependencies`` sections lists all C libraries this package
  depends on.

  Compiler and linker flags are found by running ``mys-config`` or
  ``pkg-config`` commands. ``mys-config`` is used if found, otherwise
  ``pkg-config`` is used.

  Run ``mys/pkg-config <package> --cflags`` and ``mys/pkg-config
  <package> --libs`` to get compiler and linker flags.
