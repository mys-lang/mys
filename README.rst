|buildstatus|_
|coverage|_

🐁 Mys
======

The Mys (/maɪs/) programming language - an attempt to create a
statically typed Python-like language that produces fast binaries.

Mys is heavily inspired by Python's syntax and Rust's packaging.

Project homepage: https://github.com/eerimoq/mys

🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧
🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧

**IMPORTANT INFORMATION**

Mys is currently this README (the language specification), the
`examples`_ folder that contains Mys packages, and the `tests`_ folder
that contains Mys source code (``.mys``) and it's manually written
"generated" C++ code (``.mys.cpp``).

The language and build system implementation is hardcoded to build and
run the Hello World appliaction, so it's not yet useful to anyone.

🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧
🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧

Installation
------------

.. code-block:: python

   $ pip install mys

You must also have a recent versions of ``g++`` and ``make``
installed.

Tutorial
--------

First of all, create a package called ``foo`` and enter it. This
package is used in throughout the tutorial.

.. code-block::

   $ mys new foo
   $ cd foo

Two files are created; ``Package.toml`` and
``src/main.mys``. ``Package.toml`` contains the package configuration
and ``src/main.mys`` the application source code.

The source code is the hello world application looks like this:

.. code-block:: python

   def main():
       print('Hello, world!')

Build and run the application with ``mys run``. It prints ``Hello,
world!``, just as expected.

.. code-block::

   $ mys run
   Hello, world!

Replace the code in ``src/main.mys`` with the code below. It
examplifies how to use functions, classes, exceptions, types and
command line arguments. The syntax is almost identical to Python, so
most readers should easily understand it.

.. code-block:: python

   def func_1(a: int) -> (int, Final[str]):
       return 2 * a, 'Bar'


   def func_2(a: int, b: int=1) -> int:
       for i in range(b):
           a += i * b

       return a


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


   class Calc:

       def __init__(self, value: int):
           self.value = value

       def triple(self):
           self.value *= 3


   def main(args: [str]):
       value = int(args[1])
       print('func_1(value):', func_1(value))
       print('func_2(value):', func_2(value))
       print('func_3(None): ', func_3(None))
       print('func_3(value):', func_3(value))
       print('func_4(value):', func_4(value))
       func_5()
       calc = Calc(value)
       calc.triple()
       print('calc:         ', calc)

Build and run it.

.. code-block::

   $ mys run 5
   func_1(value): (5, 'Bar')
   func_2(value): 7
   func_3(None):  0
   func_3(value): 10
   func_4(value): {1: [], 50: [7.5, -1,0]}
   func_5():      An exception occurred.
   calc:          Calc(value=15)

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

All built-ins aims to behave like their Python counterparts, with the
following differences.

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

Variables declared as ``Final`` can't be modified.

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
allocated on the heap and managed by `C++ shared pointers`_. Objects
that are known not to outlive a function are allocated on the stack.

There is no garbage collector, as there is no garbage to
collect. Reference counting is used instead.

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

- Generators are not supported.

- The majority of the standard library is not implemented.

- Dictionary keys must be integers, floats, strings or bytes.

- Strings, bytes and tuple items are **mutable** by default. Mark them
  as ``Final`` to make them immutable.

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

ToDo: Create a benchmark and present its outcome in this section.

Build time
^^^^^^^^^^

Mys should be slower.

Startup time
^^^^^^^^^^^^

Mys should be faster.

Runtime
^^^^^^^

Mys should be faster.

Memory usage
^^^^^^^^^^^^

Mys should use less memory.

Build process
-------------

``mys run`` and ``mys build`` does the following:

#. Uses Python's parser to transform the source code to an Abstract
   Syntax Tree (AST).

#. Generates C++ code from the AST.

#. Compiles the C++ code with ``g++``.

#. Statically links the program with ``g++``.

.. |buildstatus| image:: https://travis-ci.com/eerimoq/mys.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/mys

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/mys/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/mys

.. _official Visual Code guide: https://code.visualstudio.com/docs/languages/overview#_adding-a-file-extension-to-a-language

.. _C++ shared pointers: https://en.cppreference.com/w/cpp/memory/shared_ptr

.. _examples: https://github.com/eerimoq/mys/tree/master/examples

.. _tests: https://github.com/eerimoq/mys/tree/master/tests/files
