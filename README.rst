|buildstatus|_
|coverage|_

Mys
===

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

The Mys programming language - an attempt to create a strongly typed
Python-like language that produces fast binaries.

Project homepage: https://github.com/eerimoq/mys

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

Installation
------------

.. code-block:: python

   $ pip install mys

Tutorial
--------

First of all, create a package called ``foo`` and enter it. This
package is used in throughout the tutorial.

.. code-block:: shell

   $ mys new foo
   $ cd foo

Two files are create; ``Package.toml`` and
``src/main.mys``. ``Package.toml`` contains the package configuration
and ``src/main.mys`` the application source code.

The source code is the hello world application.

.. code-block:: python

   def main():
       print('Hello, world!')

Build and run it with ``mys run``. All build output is found in the
``build`` directory.

.. code-block:: shell

   $ mys run
   Hello, world!

Now, replace the code in ``src/main.mys`` with the code below.

.. code-block:: python

   def func_1(a: int) -> (int, str):
        return 2 * a, 'Bar'

   def func_2(a: int, b: int=1) -> int:
        return a * b

   def func_3(a: Optional[int]) -> int:
       if a is None:
           return 0
       else:
           return 2 * a

   def func_4(a: int) -> {int: [float]}:
       return {10 * a: [7.5, -1.0]}

   def main(args: [str]):
       value = int(args[1])
       print('func_1:', func_1(value))
       print('func_2:', func_2(value))
       print('func_3:', func_3(None)))
       print('func_3:', func_3(value))
       print('func_4:', func_4(value))

Build and run it.

.. code-block:: shell

   $ mys run 5
   func_1: (5, 'Bar')
   func_2: 5
   func_3: 0
   func_3: 10
   func_4: {50: [7.5, -1,0]}

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
