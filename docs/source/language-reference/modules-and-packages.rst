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
   ├── README.rst
   └── src/
       ├── lib.mys
       └── main.mys         # Only part of packages that can build executables.
