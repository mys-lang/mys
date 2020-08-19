|buildstatus|_
|coverage|_

Mys
===

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

Strongly typed Python to C++ transpiler.

Project homepage: https://github.com/eerimoq/mys

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

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

Using types defined in the standard library typing module where
possible.

Variables may all be set to ``None`` if declared as ``Optional``.

+---------------+--------------------------------------------+
| Python Type   | Mys Type                                   |
+===============+============================================+
| ``int``       | ``u8``, ``u16``, ``u32``, ``u64``          |
+---------------+--------------------------------------------+
| ``int``       | ``s8``, ``s16``, ``s32``, ``s64``          |
+---------------+--------------------------------------------+
| ``float``     | ``f32``, ``f64``                           |
+---------------+--------------------------------------------+
| ``str``       | ``str``                                    |
+---------------+--------------------------------------------+
| ``bytes``     | ``bytes``                                  |
+---------------+--------------------------------------------+
| ``bytearray`` | ``bytearray``                              |
+---------------+--------------------------------------------+
| ``tuple``     | ``Tuple``                                  |
+---------------+--------------------------------------------+
| ``list``      | ``List``                                   |
+---------------+--------------------------------------------+
| ``dict``      | ``Dict``                                   |
+---------------+--------------------------------------------+
| ``set``       | ``Set``                                    |
+---------------+--------------------------------------------+

Resources
---------

https://github.com/python/mypy/blob/master/test-data/unit/pythoneval.test

.. |buildstatus| image:: https://travis-ci.com/eerimoq/mys.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/mys

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/mys/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/mys
