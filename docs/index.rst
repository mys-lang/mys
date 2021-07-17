|discord|_
|test|_

The Mys programming language
============================

.. warning::

   Mys is still in the very early stages of development. API:s will
   change, so now is the time to make suggestions! Join the `Mys
   Discord server`_ to get in touch with the developers!

The Mys (/maɪs/) programming language - an attempt to create a
statically typed compiled Python-like language that produces fast
binaries.

Mys is heavily inspired by Python's syntax and Rust's packaging.

Source code:

.. code-block:: python

   from random.pseudo import random

   def main():
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

Project
-------

- `GitHub`_: Mys' official project repository with source code and issue tracker.

Community
---------

- `Discord`_: Mys' official Discord server.

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   user-guide
   developer-guide
   language-reference
   standard-library
   credits
   statistics

.. |discord| image:: https://img.shields.io/discord/777073391320170507?label=Discord&logo=discord&logoColor=white
.. _discord: https://discord.gg/GFDN7JvWKS

.. |test| image:: https://github.com/mys-lang/mys/workflows/Test/badge.svg?event=schedule
.. _test: https://github.com/mys-lang/mys/actions?query=event%3Aschedule+workflow%3ATest+

.. _Mys Discord server: https://discord.gg/GFDN7JvWKS

.. _Discord: https://discord.gg/GFDN7JvWKS

.. _GitHub: https://github.com/mys-lang/mys
