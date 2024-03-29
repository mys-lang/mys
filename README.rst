|discord|_
|test|_

WARNING
=======

Mys is still in the very early stages of development. API:s will
change, so now is the time to make suggestions! Join the `Mys Discord
server`_ to get in touch with the developers!

Mys
===

The Mys programming language - an attempt to create a statically typed
compiled Python-like language that produces fast binaries.

Mys is heavily inspired by Python's syntax and Rust's packaging.

Source code:

.. code-block:: python

   from random.pseudo import random

   func main():
       print(random())

Package configuration:

.. code-block:: toml

   [package]
   name = "robot"
   version = "0.1.0"
   authors = ["Mys Lang <mys.lang@example.com>"]

   [dependencies]
   random = "latest"

Mys is mainly targeting resource constrained single core embedded
systems, but is just as useful in desktop environments.

Documentation
-------------

- `Getting Started`_: Step by step guide to get you started writing
  applications in Mys.

- `The Mys documentation`_: Mys' official documentation. The best
  place to start learning Mys.

Community
---------

- `Discord`_: Mys' official Discord server.

Contributing
------------

There are many ways in which you can participate in the project, for
example:

- Submit bugs and feature requests.

- Fix bugs and implement new features.

- Review the documentation and make pull requests for anything from
  typos to new content.

There is more information available in the `Mys Developer Guide`_.

.. |discord| image:: https://img.shields.io/discord/777073391320170507?label=Discord&logo=discord&logoColor=white
.. _discord: https://discord.gg/GFDN7JvWKS

.. |test| image:: https://github.com/mys-lang/mys/workflows/Test/badge.svg?event=schedule
.. _test: https://github.com/mys-lang/mys/actions?query=event%3Aschedule+workflow%3ATest+

.. _The Mys documentation: https://mys-lang.org/

.. _Mys Discord server: https://discord.gg/GFDN7JvWKS

.. _Discord: https://discord.gg/GFDN7JvWKS

.. _Mys Developer Guide: https://mys-lang.org/developer-guide.html

.. _GitHub: https://github.com/mys-lang/mys

.. _Getting Started: https://mys-lang.org/user-guide/getting-started.html
