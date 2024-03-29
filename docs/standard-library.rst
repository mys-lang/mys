Standard Library
================

There is no standard library part of the installation. Functionality
classically in the standard library and functionality in third party
packages are considered equally important and are all
downloaded/copied and built automatically when listed as dependencies
to your package.

Using
-----

To use packages in your project, just add them to the dependencies
section in your ``package.toml``-file.

.. code-block:: toml

   [dependencies]
   random = "latest"
   base64 = "latest"

Publishing
----------

Publish a package by running ``mys publish`` in your package's root
folder. A token is printed the first time a package is published. This
token is required to publish the package again, so make sure to save
it. Run ``mys publish -t <token>`` to publish with a token.

Delete a published package with ``mys delete <package> <token>``.

Packages
--------

Number of packages: {website-number-of-packages}

Number of downloads: {website-number-of-downloads}

{website-packages}

API
---

There is a `GraphQL`_ end-point, https://mys-lang.org/graphql, that
provides standard library information.

.. _GraphQL: https://graphql.org
