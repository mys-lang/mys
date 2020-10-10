|buildstatus|_
|coverage|_

🐁 Mys
======

The Mys (/maɪs/) programming language - an attempt to create a
statically typed Python-like language that produces fast binaries.

Mys is heavily inspired by Python's syntax and Rust's packaging.

.. code-block:: python

   from random.pseudo import random

   def main():
       print(random())

.. code-block:: toml

   [package]
   name = "robot"
   version = "0.1.0"

   [dependencies]
   random = "*"

Mys is mainly targeting resource constrained single and multi core
embedded systems.

Project homepage: https://github.com/eerimoq/mys

🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧
🚧 🚧 🚧 🚧 🚧 🚧 🚧

**IMPORTANT INFORMATION**

The language and build system implementation is still in a very early
stage. Some arithmetic, print and conditional statements works, but
not much more.

🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧 🚧
🚧 🚧 🚧 🚧 🚧 🚧 🚧

Quick start
-----------

.. image:: https://github.com/eerimoq/mys/raw/master/docs/quick-start.gif

Installation
------------

Install Python 3.6 or later, and then install Mys using ``pip``.

.. code-block:: python

   $ pip install mys

You must also have recent versions of ``g++``, ``make`` and
``pylint`` installed.

Tutorial
--------

First of all, create a package called ``foo`` with the command ``mys
new foo``, and then enter it. This package is used in throughout the
tutorial.

.. image:: https://github.com/eerimoq/mys/raw/master/docs/new.png

``src/main.mys`` implements the hello world application. This file is
only part of application packages (executables).

.. code-block:: python

   def main():
       print("Hello, world!")

Build and run the application with the command ``mys run``. It prints
``Hello, world!``, just as expected.

.. image:: https://github.com/eerimoq/mys/raw/master/docs/run.png

``src/lib.mys`` implements the function ``add()`` and it's test
``test_add()``. This file is normally part of both application and
library packages.

.. code-block:: python

   def add(first: i32, second: i32) -> i32:
       return first + second

   @test
   def test_add():
       assert_eq(add(1, 2), 3)

Build and run the tests with the command ``mys test``.

.. image:: https://github.com/eerimoq/mys/raw/master/docs/test.png

Add the `bar package`_ as a dependency and use it's ``hello()``
function.

``package.toml`` with the ``bar`` dependency added:

.. code-block:: toml

   [package]
   name = "foo"
   version = "0.1.0"
   authors = ["Mys Lang <mys.lang@example.com>"]

   [dependencies]
   bar = "*"

``src/main.mys`` importing ``hello()`` from the ``bar`` module:

.. code-block:: python

   from bar import hello

   def main(args: [string]):
       hello(args[1])

Build and run the new application. Notice how the dependency is
downloaded and that ``mys run universe`` prints ``Hello, universe!``.

.. image:: https://github.com/eerimoq/mys/raw/master/docs/run-universe.png

Replace the code in ``src/main.mys`` with the code below. It
examplifies how to use functions, classes, exceptions, types and
command line arguments. The syntax is almost identical to Python, so
most readers should easily understand it.

**NOTE**: This code does not yet work. This is just an example of what
an application could look like in the future. The `Fibonacci example`_
works, so try that instead!

.. code-block:: python

   def func_1(a: i32) -> (i32, string):
       return 2 * a, "Bar"

   def func_2(a: i32, b: i32 = 1) -> i32:
       for i in range(b):
           a += i * b

       return a

   def func_3(a: i32) -> {i32: [f32]}:
       return {
           1: [],
           10 * a: [7.5, -1.0]
       }

   def func_4():
       try:
           raise Error()
       except:
           print("func_4():      An error occurred.")

   def func_5() -> [i32]:
       small: [i32] = []

       for v in [3, 1, 5, 7, 2]:
           if v < 5:
               small.append(v)

       small.sort()
       small.reverse()

       return small

   class Calc:

       value: i32

       def triple(self):
           self.value *= 3

   def main(args: [string]):
       value = i32(args[1])
       print("func_1(value):", func_1(value))
       print("func_2(value):", func_2(value))
       print("func_3(value):", func_3(value))
       func_4()
       print("func_5():     ", func_5())
       calc = Calc(value)
       calc.triple()
       print("calc:         ", calc)

Build and run it.

.. code-block::

   $ mys run 5
   func_1(value): (5, "Bar")
   func_2(value): 7
   func_3(value): {1: [], 50: [7.5, -1,0]}
   func_4():      An error occurred.
   func_5():      [3, 2, 1]
   calc:          Calc(value=15)

Types
-----

+-----------------------------------+-----------------------+----------------------------------------------------------+
| Type                              | Example               | Comment                                                  |
+===================================+=======================+==========================================================+
| ``i8``, ``i16``, ``i32``, ``i64`` | ``1``, ``-1000``      | Signed integers of 8, 16, 32 and 64 bits.                |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``u8``, ``u16``, ``u32``, ``u64`` | ``1``, ``1000``       | Unsigned integers of 8, 16, 32 and 64 bits.              |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``f32``, ``f64``                  | ``5.5``, ``-100.0``   | Floating point numbers of 32 and 64 bits.                |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``bool``                          | ``True``, ``False``   | A boolean.                                               |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``char``                          | ``'a'``               | A unicode character. ``''`` is not a character.          |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``string``                        | ``"Hi!"``             | A sequence of unicode characters.                        |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``bytes``                         | ``b"\x00\x43"``       | A sequence of bytes.                                     |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``tuple(T1, T2, ...)``            | ``(5.0, 5, "foo")``   | A tuple with items of types T1, T2, etc.                 |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``list(T)``                       | ``[5, 10, 1]``        | A list with items of type T.                             |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``dict(TK, TV)``                  | ``{5: "a", -1: "b"}`` | A dictionary with keys of type TK and values of type TV. |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``class Name``                    | ``Name()``            | A class.                                                 |
+-----------------------------------+-----------------------+----------------------------------------------------------+

i8, i16, i32, i64, u8, u16, u32 and u64
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   # number is [0-9]+, 0x[0-9a-f]+ or 0b[0-1]+
   i8/i16/i32/i64(number: string)
   u8/u16/u32/u64(number: string)

   i8/i16/i32/i64(number: f32/f64)
   u8/u16/u32/u64(number: f32/f64)
   i8/i16/i32/i64(number: bool)
   u8/u16/u32/u64(number: bool)

f32 and f64
^^^^^^^^^^^

.. code-block:: text

   f32/f64(number: string)
   f32/f64(number: i8/i16/i32/i64/u8/u16/u32/u64)
   f32/f64(number: bool)

char
^^^^

.. code-block:: text

   char(number: i8/i16/i32/i64/u8/u16/u32/u64)

string
^^^^^^

.. code-block:: text

   string(length: u32)                 # Reserve space for given number of characters.
   string(character: char)             # From a character.
   string(utf8: bytes)                 # From UTF-8 bytes.
   string(parts: [string])             # From list of strings.
   to_utf8() -> bytes                  # To UTF-8 bytes.
   +=(value: string)                   # Append a string.
   +=(value: char)                     # Append a character.
   +(value: string) -> string          # Add a string.
   +(value: char) -> string            # Add a character.
   []=(index: u64, character: char)    # Set a character.
   [](index: u64) -> char              # Get a character.
   []=(begin: u64,                     # Set a substring.
       end: u64,
       step: u64,
       value: string)
   [](begin: u64,                      # Get a substring.
      end: u64,
      step: u64) -> string
   __in__(value: char) -> bool         # Contains character.
   __in__(value: string) -> bool       # Contains string.
   lines() -> [string]                 # A list of lines.
   split(separator: char) -> [string]
   strip(chars: string)                # Strip leading and trailing characters in place.

bytes
^^^^^

.. code-block:: text

   bytes(length: u32)           # Reserve space for given number of bytes.
   bytes(hex: string)           # From a hexadecimal string.
   to_hex() -> string           # To a hexadecimal string.
   +=(value: bytes)             # Append bytes.
   +=(value: u8)                # Append a number.
   +(value: bytes) -> bytes     # Add bytes.
   +(value: u8) -> bytes        # Add a number.
   []=(index: u64, value: u8)
   [](index: u64) -> u8
   []=(begin: u64,              # Set subbytes.
       end: u64,
       step: u64,
       value: bytes)
   [](begin: u64,               # Get subbytes.
      end: u64,
      step: u64) -> bytes
   __in__(value: u8) -> bool    # Contains value.

tuple
^^^^^

.. code-block:: text

   []=(index: u64, item: TN)  # Set item at index. The index  must be known at compile time.
   [](index: u64) -> TN       # Get item at index. The index must be known at compile time.

list
^^^^

.. code-block:: text

   list(length: u32)           # Reserve space for given number of items.
   +=(value: [T])              # Append a list.
   +=(value: T)                # Append an item.
   []=(index: u64, item: T)
   [](index: u64) -> T
   []=(begin: u64,             # Set a sublist.
       end: u64,
       step: u64,
       value: [T])
   [](begin: u64,              # Get a sublist.
      end: u64,
      step: u64) -> [T]
   __in__(item: T) -> bool     # Contains item.
   sort()                      # Sort items in place.
   reverse()                   # Reverse items in place.

dict
^^^^

.. code-block:: text

   [TK] -> TV                     # Set value for key.
   __in__(key: TK) -> bool        # Contains given key.

Built-in functions
------------------

+-----------------+--------------------------+----------------------------------------------------+
| Name            | Example                  | Comment                                            |
+=================+==========================+====================================================+
| ``open()``      | ``open("path/to/file")`` | Opens given file in given mode.                    |
+-----------------+--------------------------+----------------------------------------------------+
| ``print()``     | ``print("Hi!")``         | Prints given data.                                 |
+-----------------+--------------------------+----------------------------------------------------+
| ``range()``     | ``range(10)``            | A range of numbers.                                |
+-----------------+--------------------------+----------------------------------------------------+

Packages
--------

A package contains modules that other packages can use. All packages
contains a file called ``lib.mys``, which is imported from with ``from
<package> import <function/class/variable>``.

There are two kinds of packages; library packages and application
packages. The only difference is that application packages contains a
file called ``src/main.mys``, which contains the application entry
point ``def main(...)``. Application packages produces an executable
when built (``mys build``), libraries does not.

A package:

.. code-block:: text

   my-package/
   ├── LICENSE
   ├── package.toml
   ├── pylintrc
   ├── README.rst
   └── src/
       ├── lib.mys
       └── main.mys         # Only part of application packages.

The mys command line interface:

.. code-block:: text

   mys new      Create a new package.
   mys build    Build the appliaction.
   mys run      Build and run the application.
   mys test     Build and run tests.
   mys clean    Remove build output.
   mys lint     Perform static code analysis.
   mys publish  Publish a release.

Importing functions and classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import functions, classes and variables from other packages with
``from <package>[[.<sub-package>]*.<module>] import
<function/class/variable>``.

Import functions, classes and variables from current package with
``from .+[[<sub-package>.]*<module>] import
<function/class/variable>``. One ``.`` per directory level.

Use ``from ... import ... as <name>`` to use a custom name.

Here are a few examples:

.. code-block:: python

   from mypkg1 import func1
   from mypkg2.subpkg1.mod1 import func2 as func3
   from mypkg2 import Class1
   from mypkg2 import var1
   from .mod1 import func4           # ../mod1.mys
   from ...mypkg3.mod1 import func5  # ../../../mypkg3/mod1.mys

   def foo():
       func1()
       func3()
       Class1()
       print(var1)
       func4()
       func5()

List of packages
^^^^^^^^^^^^^^^^

- `argparse`_ - Command line argument parser.

- `log`_ - Logging facilities.

- `math`_ - Basic math operations.

- `random`_ - Random numbers.

- `system`_ - System services.

- `time`_ - Date and time.

Extending Mys with C++
----------------------

Extending Mys with C++ is extremly easy and flexible. Strings that
starts with ``mys-embedded-c++`` are inserted at the same location in
the generated code.

.. code-block:: python

   def main():
       a: i32 = 0

       """mys-embedded-c++

       i32 b = 2;
       a++;
       """

       print("a + b:", a + b)

Loops
-----

``while`` and ``for`` loops are available.

``while`` loops run until given condition is false or until
``break``.

``for`` loops can only iterate over ranges, lists, dictionaries,
strings and bytes. Each item index is optionally available.

.. code-block:: python

   # While.
   v = 0

   while v < 10:
       if v < 3:
           continue
       elif v == 7:
           break

       v += 1

   # Ranges.
   for v in range(10):
       if v < 3:
           continue
       elif v == 7:
           break

   for i, v in range(4, 10, -2):
       pass

   # Lists.
   for v in [3, 1]:
       pass

   for i, v in [3, 1]:
       pass

   # Dictionaries.
   for k, v in {2: 5, 6: 2}:
       pass

   for i, k, v in {2: 5, 6: 2}:
       pass

   # Strings.
   for c in "foo":
       pass

   for i, c in "foo":
       pass

   # Bytes.
   for b in b"\x03\x78":
       pass

   for i, b in b"\x03\x78":
       pass

Memory management
-----------------

Integers and floating point numbers are allocated on the stack, passed
by value to functions and returned by value from functions, just as
any C++ program.

Strings, bytes, tuples, lists, dicts and classes are normally
allocated on the heap and managed by `C++ shared pointers`_. Objects
that are known not to outlive a function are allocated on the stack.

Reference cycles are not detected and will result in memory leaks.

There is no garbage collector.

Classes
-------

- Instance members are accessed with ``self.<variable/method>``.

- Overridden methods must be decorated with ``@override``.

- Automatically added methods (``__init__()``, ``__str__()``, ...)
  are only added if missing.

Below is a class with a data member ``value`` and a method
``inc()``.

The constructor ``def __init__(self, value: i32 = 0)`` (and more
methods) are automatically added to the class as they are missing.

.. code-block:: python

   class Foo:

       value: i32

       def inc(self):
           self.value += 1

   def main():
       print("f1:")
       f1 = Foo()
       print(f1)
       f1.inc()
       print(f1)

       print("f2:")
       f2 = Foo(5)
       print(f2)

.. code-block:: text

   $ mys run
   f1:
   Foo(value=0)
   Foo(value=1)
   f2:
   Foo(value=5)

Build options
-------------

``--optimize {speed, size, debug}``: Optimize the build for given
level. Optimizes for speed by default.

``--unsafe``: Disable runtime safety checks for faster and smaller
binaries.

Disables:

- Implicit ``None`` checks.

- ``list``, ``string`` and ``bytes`` out of bounds checks.

- Signed integer overflow checks.

- Default variable and data member initializations.

- Message ownership checks.

Message passing
---------------

See `examples/wip/message_passing`_ for some ideas.

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

Build process
-------------

``mys build``, ``mys run`` and ``mys test`` does the following:

#. Use Python's parser to transform the source code to an Abstract
   Syntax Tree (AST).

#. Generate C++ code from the AST.

   Probably generate three files:

   - ``<module>.mys.types.hpp``, which contains forward declarations
     of all types.

   - ``<module>.mys.hpp``, which contains all declarations.

   - ``<module>.mys.cpp``, which contains the implementation.

   Goals:

   - Only make methods virtual if overridden by another class.

#. Compile the C++ code with ``g++``.

#. Link the application with ``g++``.

.. |buildstatus| image:: https://travis-ci.com/eerimoq/mys.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/mys

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/mys/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/mys

.. _official Visual Code guide: https://code.visualstudio.com/docs/languages/overview#_adding-a-file-extension-to-a-language

.. _C++ shared pointers: https://en.cppreference.com/w/cpp/memory/shared_ptr

.. _examples: https://github.com/eerimoq/mys/tree/master/examples

.. _tests: https://github.com/eerimoq/mys/tree/master/tests/files

.. _Fibonacci example: https://github.com/eerimoq/mys/blob/master/examples/fibonacci/src/main.mys

.. _bar package: https://github.com/eerimoq/mys-bar

.. _examples/wip/message_passing: https://github.com/eerimoq/mys/tree/master/examples/wip/message_passing

.. _argparse: https://github.com/eerimoq/mys-argparse

.. _log: https://github.com/eerimoq/mys-log

.. _math: https://github.com/eerimoq/mys-math

.. _random: https://github.com/eerimoq/mys-random

.. _system: https://github.com/eerimoq/mys-system

.. _time: https://github.com/eerimoq/mys-time
