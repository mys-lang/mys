The mys command
---------------

The mys command has the following subcommands:

.. code-block:: text

   mys new      Create a new package.
   mys build    Build the appliaction.
   mys run      Build and run the application.
   mys test     Build and run tests.
   mys clean    Remove build output.
   mys publish  Publish a release.
   mys install  Install an application from local package or registry.

Build options
^^^^^^^^^^^^^

``--optimize {speed, size, debug}``: Optimize the build for given
level. Optimizes for speed by default.

``--unsafe``: Disable runtime safety checks for faster and smaller
binaries.

.. warning::

   ``--unsafe`` is not yet implemented.

Disables:

- Implicit ``None`` checks.

- ``list``, ``string`` and ``bytes`` out of bounds checks.

- Signed integer overflow checks.

- Default variable and data member initializations.

- Message ownership checks.

``--no-ccache``: Do not use `Ccache`_.

Configuration
^^^^^^^^^^^^^

The mys command line tool can be configured to fit your development
environment.

NOTE: It's currently not possible to configure anything.

Search order:

#. The environment variable ``MYS_CONFIG``.

#. The file ``~/.config/mys/config.toml``

.. _Ccache: https://ccache.dev/
