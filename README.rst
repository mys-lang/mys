|buildstatus|_
|coverage|_

Mys
===

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

Strongly typed Python to C++17 transpiler.

Project homepage: https://github.com/eerimoq/mys

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

Installation
------------

.. code-block:: python

   $ pip install mys

Goals
-----

- Blazingly fast programs written in Python.

- Small statically linked binary.

- No GIL, mainly to allow threads to run in parallel. However, data
  races will occur when multiple threads uses a variable at the same
  time, which will likely make the program crash.

Limitations
-----------

- All elements in a list must have the same type.

- All items in a dict must have the same key and value types. Key and
  value may be different types.

- All items in a set must have the same type.

- Max 64 bits integers.

- 32 and 64 bits floats.

- No decorators.

- No dynamic properties (getattr, setattr, eval, ...).

- No async.

- ...

Types
-----

Using types defined in the standard library typing module where
possible.

Variables may all be set to ``None`` if declared as ``Optional``.

C++ ``auto`` is used in the generated code if the type is omitted.

+---------------+-----------------------------------+
| Python Type   | Mys Type                          |
+===============+===================================+
| ``int``       | ``u8``, ``u16``, ``u32``, ``u64`` |
+---------------+-----------------------------------+
| ``int``       | ``s8``, ``s16``, ``s32``, ``s64`` |
+---------------+-----------------------------------+
| ``float``     | ``f32``, ``f64``                  |
+---------------+-----------------------------------+
| ``str``       | ``str``                           |
+---------------+-----------------------------------+
| ``bytes``     | ``bytes``                         |
+---------------+-----------------------------------+
| ``bytearray`` | ``bytearray``                     |
+---------------+-----------------------------------+
| ``tuple``     | ``Tuple``                         |
+---------------+-----------------------------------+
| ``list``      | ``List``                          |
+---------------+-----------------------------------+
| ``dict``      | ``Dict``                          |
+---------------+-----------------------------------+
| ``set``       | ``Set``                           |
+---------------+-----------------------------------+

Examples
--------

Hello world
^^^^^^^^^^^

.. code-block:: python

   def main():
       print('Hello, world!')

Basics
^^^^^^
       
.. code-block:: python
                
   def foo(a: s32) -> Tuple[s32, str]:
        return 2 * a, 'Bar'

   def main(args: List[str]):
       print(foo(s32(args[1])))
       
Performance
-----------

ToDo.

Resources
---------

https://github.com/python/mypy/blob/master/test-data/unit/pythoneval.test

https://medium.com/@konchunas/monkeytype-type-inference-for-transpiling-python-to-rust-64fa5a9eb966

http://blog.madhukaraphatak.com/functional-programming-in-c++/

https://github.com/Instagram/MonkeyType

Similar projects
----------------

https://github.com/konchunas/pyrs

https://github.com/lukasmartinelli/py14

https://github.com/shedskin/shedskin

https://github.com/pradyun/Py2C

https://github.com/mbdevpl/transpyle

http://numba.pydata.org/

https://github.com/Nuitka/Nuitka

https://github.com/QQuick/Transcrypt

https://github.com/pyjs/pyjs

.. |buildstatus| image:: https://travis-ci.com/eerimoq/mys.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/mys

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/mys/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/mys
