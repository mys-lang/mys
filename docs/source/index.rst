|discord|_
|test|_

Welcome to Mys' documentation!
==============================

.. warning::

   Mys is still in the very early stages of development. API:s will
   change, so now is the time to make suggestions! Join the `Mys
   Discord server`_ to get in touch with the developers!

The Mys (/maɪs/) programming language - an attempt to create a
statically typed Python-like language that produces fast binaries.

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
   random = "*"

Mys is mainly targeting resource constrained single and multi core
embedded systems, but is just as useful in desktop environments.

Project
-------

- `GitHub`_: Mys' official project repository.

Community
---------

- `Discord`_: Mys' official Discord server.

Notable differences to Python
-----------------------------

- Traits instead of classic inheritence.

- Statically typed.

- Bytes and strings are mutable.

- Integers are bound (i32, u32, i64, ...).

- Iterators/generators do not (yet?) exist.

- Rust-like generic functions and classes.

- Only packages. No stand alone modules.

- Compiled to machine code. No interpreter.

- Data races and memory corruption possible, but unlikely.

- No async.

- Only ``from ... import ...`` is allowed. ``import ...`` is not.

- Only functions, enums, traits, classes and variables can be
  imported, not modules.

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :hidden:

   user-guide
   developer-guide
   documentation
   credits

.. |discord| image:: https://img.shields.io/discord/777073391320170507?label=Discord&logo=discord&logoColor=white
.. _discord: https://discord.gg/GFDN7JvWKS

.. |test| image:: https://github.com/mys-lang/mys/workflows/Test/badge.svg?event=schedule
.. _test: https://github.com/mys-lang/mys/actions?query=workflow%3ATest

.. _Mys Discord server: https://discord.gg/GFDN7JvWKS

.. _Discord: https://discord.gg/GFDN7JvWKS

.. _GitHub: https://github.com/mys-lang/mys
