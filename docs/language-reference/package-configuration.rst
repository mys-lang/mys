Package configuration
---------------------

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
   os = "latest"
   sys = { path = "../.." }

   [c-dependencies]
   sqlite3 = "latest"

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

  Compiler and linker flags are found by executing ``mys-config`` or
  ``pkg-config``. ``mys-config`` is used if found in path, otherwise
  ``pkg-config`` is used.

  The build system executes ``mys/pkg-config <package> --cflags`` and
  ``mys/pkg-config <package> --libs`` to get compiler and linker
  flags.
