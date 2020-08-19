|buildstatus|_
|coverage|_

Mys
===

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

Strongly typed Python to C++ transpiler.

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

Project homepage: https://github.com/eerimoq/mys

Installation
------------

.. code-block:: python

   $ pip install mys

Limitations
-----------

- All elements in a list must have the same type.

- Max 64 bits integers.

- 32 and 64 bits floats.

- Decorators are not supported.
  
Types
-----

u8, u16, u32, u64, s8, s16, s32, s64, f32, f64, str, bytes, bytearray,
set, dict, list, tuple, object

Resources
---------

https://github.com/python/mypy/blob/master/test-data/unit/pythoneval.test

.. |buildstatus| image:: https://travis-ci.com/eerimoq/mys.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/mys

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/mys/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/mys
