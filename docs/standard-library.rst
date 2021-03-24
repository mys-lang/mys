Standard Library
================

The is no standard library part of the installation. Functionality
classically in the standard library and functionality in third party
packages are considered equally important and are all
downloaded/copied and built automatically when listed as dependencies
to your package.

To use packages in your project, just add them to the dependencies
section in your ``package.toml``-file.

.. code-block:: toml

   [dependencies]
   random = "latest"
   base64 = "latest"

Some packages
^^^^^^^^^^^^^

.. warning:: Some packages works, some does not even compile. Big work
             in progress!

- {website-package}
