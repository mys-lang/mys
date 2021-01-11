The mys tool
------------

Build options
^^^^^^^^^^^^^

``--optimize {speed, size, debug}``: Optimize the build for given
level. Optimizes for speed by default.

``--unsafe``: Disable runtime safety checks for faster and smaller
binaries. **This is not yet implemented.**

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
