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
       print('func_1(value):', func_1(value))
       print('func_2(value):', func_2(value))
       print('func_3(None): ', func_3(None))
       print('func_3(value):', func_3(value))
       print('func_4(value):', func_4(value))

Build and run it.

.. code-block:: shell

   $ mys run 5
   func_1(value): (5, 'Bar')
   func_2(value): 5
   func_3(None):  0
   func_3(value): 10
   func_4(value): {50: [7.5, -1,0]}

Built-in functions and classes
------------------------------

+-----------------------------------------------------------------------------+
| Built-in functions and classes                                              |
+=============+=============+================+==============+=================+
| ``abs()``   | ``all()``   | ``any()``      | ``bool()``   | ``bytearray()`` |
+-------------+-------------+----------------+--------------+-----------------+
| ``bytes()`` | ``chr()``   | ``dict()``     | ``divmod()`` | ``enumerate()`` |
+-------------+-------------+----------------+--------------+-----------------+
| ``f32()``   | ``f64()``   | ``float()``    | ``format()`` | ``id()``        |
+-------------+-------------+----------------+--------------+-----------------+
| ``int()``   | ``iter()``  | ``len()``      | ``list()``   | ``min()``       |
+-------------+-------------+----------------+--------------+-----------------+
| ``max()``   | ``next()``  | ``object()``   | ``open()``   | ``ord()``       |
+-------------+-------------+----------------+--------------+-----------------+
| ``print()`` | ``range()`` | ``reversed()`` | ``round()``  | ``s8()``        |
+-------------+-------------+----------------+--------------+-----------------+
| ``s16()``   | ``s32()``   | ``s64()``      | ``set()``    | ``str()``       |
+-------------+-------------+----------------+--------------+-----------------+
| ``sum()``   | ``tuple()`` | ``u8()``       | ``u16()``    | ``u32()``       |
+-------------+-------------+----------------+--------------+-----------------+
| ``u64()``   | ``zip()``   |                |              |                 |
+-------------+-------------+----------------+--------------+-----------------+

Types
-----

Variables may all be set to ``None`` if declared as ``Optional``.

+------------------------+-----------------------+----------------------------------------------------------+
| Type                   | Example               | Comment                                                  |
+========================+=======================+==========================================================+
| ``int``                | ``1``, ``-1000``      | An integer. Usually 32 or 64 bits.                       |
+------------------------+-----------------------+----------------------------------------------------------+
| ``u8``                 | ``5``, ``200``        | An 8 bits unsigned integer.                              |
+------------------------+-----------------------+----------------------------------------------------------+
| ``u16``                | ``5``, ``200``        | A 16 bits unsigned integer.                              |
+------------------------+-----------------------+----------------------------------------------------------+
| ``u32``                | ``5``, ``200``        | A 32 bits unsigned integer.                              |
+------------------------+-----------------------+----------------------------------------------------------+
| ``u64``                | ``5``, ``200``        | A 64 bits unsigned integer.                              |
+------------------------+-----------------------+----------------------------------------------------------+
| ``s8``                 | ``-5``, ``100``       | An 8 bits signed integer.                                |
+------------------------+-----------------------+----------------------------------------------------------+
| ``s16``                | ``-5``, ``100``       | A 16 bits signed integer.                                |
+------------------------+-----------------------+----------------------------------------------------------+
| ``s32``                | ``-5``, ``100``       | A 32 bits signed integer.                                |
+------------------------+-----------------------+----------------------------------------------------------+
| ``s64``                | ``-5``, ``100``       | A 64 bits signed integer.                                |
+------------------------+-----------------------+----------------------------------------------------------+
| ``float``              | ``5.5``, ``-100.0``   | A floating point number. Usually 32 bits.                |
+------------------------+-----------------------+----------------------------------------------------------+
| ``f32``                | ``5.3``, ``-100.0``   | A 32 bits floating point number.                         |
+------------------------+-----------------------+----------------------------------------------------------+
| ``f64``                | ``5.3``, ``-100.0``   | A 64 bits floating point number.                         |
+------------------------+-----------------------+----------------------------------------------------------+
| ``str``                | ``'Hi!'``             | A unicode string. Immutable.                             |
+------------------------+-----------------------+----------------------------------------------------------+
| ``bytes``              | ``b'\x00\x43'``       | A sequence of bytes. Immutable.                          |
+------------------------+-----------------------+----------------------------------------------------------+
| ``bytearray``          |                       | A sequence of bytes.                                     |
+------------------------+-----------------------+----------------------------------------------------------+
| ``tuple(T1, T2, ...)`` | ``(5.0, 5, 'foo')``   | A tuple with items of types T1, T2, etc. Immutable.      |
+------------------------+-----------------------+----------------------------------------------------------+
| ``list(T)``            | ``[5, 10, 1]``        | A list with items of type T.                             |
+------------------------+-----------------------+----------------------------------------------------------+
| ``dict(TK, TV)``       | ``{5: 'a', -1: 'b'}`` | A dictionary with keys of type TK and values of type TV. |
+------------------------+-----------------------+----------------------------------------------------------+
| ``set(T)``             |                       | A set with items of type T.                              |
+------------------------+-----------------------+----------------------------------------------------------+

Performance
-----------

ToDo.

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
