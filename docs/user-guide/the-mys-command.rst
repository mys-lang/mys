The mys command
---------------

The mys command has the following subcommands:

.. code-block:: text

   new      Create a new package.
   build    Build the appliaction.
   run      Build and run the application.
   test     Build and run tests
   clean    Remove build output.
   publish  Publish a release.
   delete   Delete a package from the registry.
   install  Install an application from local package or registry.
   doc      Build the documentation.
   style    Code styling.

Build options
^^^^^^^^^^^^^

``--optimize {speed, size, debug}``: Optimize the build for given
level. Optimizes for speed by default.

``--unsafe``: Disable runtime safety checks for faster and smaller
binaries.

.. warning::

   ``--unsafe`` is not yet fully implemented.

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

.. warning::

   It's currently not possible to configure anything.

Search order:

#. The environment variable ``MYS_CONFIG``.

#. The file ``~/.config/mys/config.toml``

.. _Ccache: https://ccache.dev/
