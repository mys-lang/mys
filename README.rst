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

.. |discord| image:: https://img.shields.io/discord/777073391320170507?label=Discord&logo=discord&logoColor=white
.. _discord: https://discord.gg/GFDN7JvWKS

.. |docstatus| image:: https://readthedocs.org/projects/mys/badge/?version=latest
.. _docstatus: https://mys.readthedocs.io/en/latest/?badge=latest

.. _Mys Discord server: https://discord.gg/GFDN7JvWKS
