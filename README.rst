|discord|_
|docstatus|_

WARNING
=======

Mys is still in the very early stages of development. API:s will
change, so now is the time to make suggestions! Join the `Mys Discord
server`_ to get in touch with the developers!

🐁 Mys
======

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

Notable differences to Python:

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



Build process
-------------

``mys build``, ``mys run`` and ``mys test`` does the following:

#. Use Python's parser to transform the source code to an Abstract
   Syntax Tree (AST).

#. Generate C++ code from the AST.

#. Compile the C++ code with ``g++``.

#. Link the application with ``g++``.

Calling mys from GNU Make recipe
--------------------------------

``mys`` uses ``make`` internally. Always prepend the command with
``+`` to share jobserver.


Mocking
-------

.. code-block:: python

   from random.pseudo import random

   def add(value: f64) -> f64:
       return value + random()

   def test_add():
       random_mock_once(5.3)
       assert add(1.0) == 6.3

.. |discord| image:: https://img.shields.io/discord/777073391320170507?label=Discord&logo=discord&logoColor=white
.. _discord: https://discord.gg/GFDN7JvWKS

.. |docstatus| image:: https://readthedocs.org/projects/mys/badge/?version=latest
.. _docstatus: https://mys.readthedocs.io/en/latest/?badge=latest

.. _Mys Discord server: https://discord.gg/GFDN7JvWKS

.. _Cygwin: https://www.cygwin.com/

.. _official Visual Code guide: https://code.visualstudio.com/docs/languages/overview#_adding-a-file-extension-to-a-language

.. _C++ shared pointers: https://en.cppreference.com/w/cpp/memory/shared_ptr

.. _examples: https://github.com/mys-lang/mys/tree/main/examples

.. _tests: https://github.com/mys-lang/mys/tree/main/tests/files

.. _Fibonacci example: https://github.com/mys-lang/mys/blob/main/examples/fibonacci/src/main.mys

.. _bar package: https://github.com/mys-lang/mys-bar

.. _examples/wip/message_passing: https://github.com/mys-lang/mys/tree/main/examples/wip/message_passing

.. _argparse: https://github.com/mys-lang/mys-argparse

.. _base64: https://github.com/mys-lang/mys-base64

.. _bits: https://github.com/mys-lang/mys-bits

.. _json: https://github.com/mys-lang/mys-json

.. _log: https://github.com/mys-lang/mys-log

.. _math: https://github.com/mys-lang/mys-math

.. _random: https://github.com/mys-lang/mys-random

.. _sqlite: https://github.com/mys-lang/mys-sqlite

.. _system: https://github.com/mys-lang/mys-system

.. _time: https://github.com/mys-lang/mys-time

.. _tests/files/various.mys: https://github.com/mys-lang/mys/blob/main/tests/files/various.mys

.. _tests/test_mys.py: https://github.com/mys-lang/mys/blob/main/tests/test_mys.py

.. _Ccache: https://ccache.dev/
