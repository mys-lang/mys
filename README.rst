|buildstatus|_
|coverage|_

🐁 Mys
======

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

The Mys (/maɪs/) programming language - an attempt to create a
strongly typed Python-like language that produces fast binaries.

Project homepage: https://github.com/eerimoq/mys

🚧 🚧 🚧 🚧 🚧 **Under construction - DO NOT USE** 🚧 🚧 🚧 🚧 🚧

Installation
------------

.. code-block:: python

   $ pip install mys

You must also have a recent version of ``g++`` installed.

Tutorial
--------

First of all, create a package called ``foo`` and enter it. This
package is used in throughout the tutorial.

.. code-block::

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

.. code-block::

   $ mys run
   Hello, world!

Now, replace the code in ``src/main.mys`` with the code below.

.. code-block:: python

   def func_1(a: int) -> (int, Final[str]):
       return 2 * a, 'Bar'


   def func_2(a: int, b: int=1) -> int:
       return a * b


   def func_3(a: Optional[int]) -> int:
       if a is None:
           return 0
       else:
           return 2 * a


   def func_4(a: int) -> {int: [float]}:
       return {
           1: [],
           10 * a: [7.5, -1.0]
       }


   def func_5():
       try:
           raise Exception()
       except:
           print('func_5():      An exception occurred.')


   def main(args: [str]):
       value = int(args[1])
       print('func_1(value):', func_1(value))
       print('func_2(value):', func_2(value))
       print('func_3(None): ', func_3(None))
       print('func_3(value):', func_3(value))
       print('func_4(value):', func_4(value))
       func_5()

Build and run it.

.. code-block::

   $ mys run 5
   func_1(value): (5, 'Bar')
   func_2(value): 5
   func_3(None):  0
   func_3(value): 10
   func_4(value): {1: [], 50: [7.5, -1,0]}
   func_5():      An exception occurred.

Built-in functions and classes
------------------------------

+--------------------------------------------------------------------------------+
| Built-in functions and classes                                                 |
+=============+=============+================+=================+=================+
| ``abs()``   | ``all()``   | ``any()``      | ``bool()``      | ``bytes()``     |
+-------------+-------------+----------------+-----------------+-----------------+
| ``chr()``   | ``dict()``  | ``divmod()``   | ``enumerate()`` | ``f32()``       |
+-------------+-------------+----------------+-----------------+-----------------+
| ``f64()``   | ``float()`` | ``format()``   | ``int()``       | ``len()``       |
+-------------+-------------+----------------+-----------------+-----------------+
| ``list()``  | ``min()``   | ``max()``      | ``open()``      | ``ord()``       |
+-------------+-------------+----------------+-----------------+-----------------+
| ``print()`` | ``range()`` | ``reversed()`` | ``round()``     | ``s8()``        |
+-------------+-------------+----------------+-----------------+-----------------+
| ``s16()``   | ``s32()``   | ``s64()``      | ``str()``       | ``sum()``       |
+-------------+-------------+----------------+-----------------+-----------------+
| ``tuple()`` | ``u8()``    | ``u16()``      | ``u32()``       | ``u64()``       |
+-------------+-------------+----------------+-----------------+-----------------+
| ``zip()``   |             |                |                 |                 |
+-------------+-------------+----------------+-----------------+-----------------+

All built-ins aims to behave like their Python counterparts, with the following differences.

- ``abs()`` only supports integer and floating point numbers.

- ``all()`` and ``any()`` only supports lists of ``bool()``.

- ``u8()``, ``u16()``, ``u32()``, ``u64()``, ``s8()``, ``s16()``,
  ``s32()`` and ``s64()`` behaves like ``int()``.

- ``f32()`` and ``f64()`` behaves like ``float()``.

- ``min()`` and ``max()`` only supports lists of integer and floating
  point numbers, and a fixed number of integer and floating points
  parameters.

- ``sum()`` only supports lists of integer and floating point numbers.

Types
-----

Variables may all be set to ``None`` if declared as ``Optional``.

+-----------------------------------+-----------------------+----------------------------------------------------------+
| Type                              | Example               | Comment                                                  |
+===================================+=======================+==========================================================+
| ``int``                           | ``1``, ``-1000``      | An integer. Usually 32 or 64 bits.                       |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``u8``, ``u16``, ``u32``, ``u64`` | ``5``, ``200``        | An 8/16/32/64 bits unsigned integer.                     |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``s8``, ``s16``, ``s32``, ``s64`` | ``-33``, ``100``      | An 8/16/32/64 bits signed integer.                       |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``float``                         | ``5.5``, ``-100.0``   | A floating point number. Usually 32 bits.                |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``f32``, ``f64``                  | ``5.3``, ``-100.0``   | A 32/64 bits floating point number.                      |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``str``                           | ``'Hi!'``             | A unicode string.                                        |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``bytes``                         | ``b'\x00\x43'``       | A sequence of bytes.                                     |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``tuple(T1, T2, ...)``            | ``(5.0, 5, 'foo')``   | A tuple with items of types T1, T2, etc.                 |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``list(T)``                       | ``[5, 10, 1]``        | A list with items of type T.                             |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``dict(TK, TV)``                  | ``{5: 'a', -1: 'b'}`` | A dictionary with keys of type TK and values of type TV. |
+-----------------------------------+-----------------------+----------------------------------------------------------+

Memory management
-----------------

Integers and floating point numbers are allocated on the stack, passed
by value to functions and returned by value from functions, just as
any C++ program.

Strings, bytes, tuples, lists, dicts and classes are normally
allocated on the heap and managed by C++ shared pointers
(`std::shared_ptr`_). Objects that are known not to outlive a function
are allocated on the stack.

There is no garbage collector.

Major differences to Python
---------------------------

- All variables must have a known type at compile time. The same
  applies to function parameters and return value.

- Threads can run in parallel. No GIL exists.

  **WARNING**: Data races will occur when multiple threads uses a
  variable at the same time, which will likely make the program crash.

- Integers and floats have a platform dependent maximum size, usually
  32 or 64 bits.

- Decorators does not exist.

- Variable function arguments ``*args`` and ``**kwargs`` are not
  supported, except to some built-in functions.

- Async is not supported.

- The majority of the standard library is not implemented.

- Dictionary keys must be integers, floats, strings or bytes.

- Strings, bytes and tuple items are **mutable**.

- Classes and functions are private by default. Decorate them with
  ``@public`` to make them public. Variables are always private.

Text editor settings
--------------------

Visual Code
^^^^^^^^^^^

Use the Python language for ``*.mys`` files by modifying your
``files.associations`` setting.

See the `official Visual Code guide`_ for more detils.

.. code-block:: json

   "files.associations": {
       "*.mys": "python"
   }

Emacs
^^^^^

Use the Python mode for ``*.mys`` files by adding the following to
your ``.emacs`` configuration file.

.. code-block:: emacs

   (add-to-list 'auto-mode-alist '("\\.mys\\'" . python-mode))

Performance
-----------

ToDo.

Build process
-------------

#. Use Python's parser to transform the source code to an Abstract
   Syntax Tree (AST).

#. Generate C++ code from the AST.

#. Compile the C++ code with ``g++``.

#. Link the program with ``g++``.

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

.. _official Visual Code guide: https://code.visualstudio.com/docs/languages/overview#_adding-a-file-extension-to-a-language

.. _std\:\:shared_ptr: https://en.cppreference.com/w/cpp/memory/shared_ptr
