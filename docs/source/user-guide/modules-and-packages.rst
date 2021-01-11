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
