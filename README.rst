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

   def main(argv: [string]):
       hello(argv[1])

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

   def main(argv: [string]):
       value = i32(argv[1])
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

Primitive types
^^^^^^^^^^^^^^^

Primitive types are always passed by value.

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

i8, i16, i32, i64, u8, u16, u32 and u64
"""""""""""""""""""""""""""""""""""""""

.. code-block:: python

   iN(number: string)             # String to signed integer.
   uN(number: string)             # String to unsigned integer.
   iN(value: f32/f64)             # Floating point number to signed integer.
   uN(value: f32/f64)             # Floating point number to unsigned integer.
   iN(value: bool)                # Boolean to signed integer (0 or 1).
   uN(value: bool)                # Boolean to unsigned integer (0 or 1).
   i32(value: char)               # Character to singed integer.
   ==                             # Comparisons.
   !=
   <
   <=
   >
   >=
   ^                              # Bitwise exclusive or.
   &                              # Bitwise and.
   |                              # Bitwise or.
   +                              # Add.
   -                              # Subtract.
   *                              # Multiply.
   /                              # Divide (round down).
   %                              # Modulus.
   ~                              # Complement.
   ^=                             # Bitwise exclusive or in place.
   &=                             # Bitwise and in place.
   |=                             # Bitwise or in place.
   +=                             # Add in place.
   -=                             # Subtract in place.
   *=                             # Multiply in place.
   /=                             # Divide in place.
   %=                             # Modulus in place.
   ~=                             # Complement in place.

f32 and f64
"""""""""""

.. code-block:: python

   fN(number: string)      # String to floating point number.
   fN(value: iN/uN)        # Integer to floating point number.
   fN(value: bool)         # Boolean to floating point number (0 or 1).
   ==                      # Comparisons.
   !=
   <
   <=
   >
   >=
   +                       # Add.
   -                       # Subtract.
   *                       # Multiply.
   /                       # Divide.
   +=                      # Add in place.
   -=                      # Subtract in place.
   *=                      # Multiply in place.
   /=                      # Divide in place.

bool
""""

.. code-block:: python

   bool(value: iN/uN)    # Integer to boolean. 0 is false, rest true.
   bool(value: f32/f64)  # Floating point number to boolean. 0.0 is false,
                         # rest true.

char
""""

.. code-block:: python

   char(number: i32)
   +=(value: i32)                    # Add given value.
   +(value: i32) -> char             # Add given value.
   -=(value: i32)                    # Subtract given value.
   -(value: i32) -> char             # Subtract given value.
   ==                                # Comparisons.
   !=
   <
   <=
   >
   >=

Complex types
^^^^^^^^^^^^^

Complex types are always passed by reference.

+-----------------------------------+-----------------------+----------------------------------------------------------+
| Type                              | Example               | Comment                                                  |
+===================================+=======================+==========================================================+
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

string
""""""

.. code-block:: python

   __init__()                              # Create an empty string. Same as "".
   __init__(character: char)               # From a character.
   __init__(other: string)                 # From a string.
   __init__(length: u64)
   length(self) -> u64                     # Its length.
   to_utf8(self) -> bytes                  # To UTF-8 bytes.
   from_utf8(utf8: bytes) -> string
   to_lower(self) -> string                # Return a new lower case string.
   to_upper(self) -> string                # Return a new upper case string.
   +=(self, value: string)                 # Append a string.
   +=(self, value: char)                   # Append a character.
   +(self, value: string) -> string        # Add a string.
   +(self, value: char) -> string          # Add a character.
   ==(self)                                # Comparisons.
   !=(self)
   <(self)
   <=(self)
   >(self)
   >=(self)
   *(self, count: u64)                     # Repeat.
   *=(self, count: u64)                    # Repeat in place.
   []=(self, index: u64, character: char)  # Set a character.
   [](self, index: u64) -> char            # Get a character.
   []=(self,                               # Set a substring.
       begin: u64,
       end: u64,
       step: u64,
       value: string)
   [](self,                                # Get a substring.
      begin: u64,
      end: u64,
      step: u64) -> string
   __in__(self, value: char) -> bool       # Contains character.
   __in__(self, value: string) -> bool     # Contains string.
   starts_with(self,
               substring: string) -> bool
   split(self,
         separator: string) -> [string]
   join(parts: [string],                   # From list of strings and separator. Inverse
        separator: string = "")            # of split().
   strip(self, chars: string)              # Strip leading and trailing characters in place.
   lower(self, self)                       # Make it lower case.
   upper(self, self)                       # Make it upper case.
   find(self,                              # Find the first occurrence of given separator
        separator: char,                   # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = -1) -> i64
   cut(self,                               # Find the first occurrence of given separator.
       separator: char) -> string          # If found, returns all characters before that,
                                           # and remove them and the separator from the
                                           # string. Returns None and leaves the string
                                           # unmodified otherwise.
   replace(self,                           # Replace old with new.
           old: char,
           new: char)
   replace(self,                           # Replace old with new.
           old: string,
           new: string)

Only ``+=`` moves existing data to the beginning of the buffer. Other
methods only changes the begin and/or end position(s). That is,
``strip()`` and ``cut()`` are cheap, but ``+=`` may have to move the
data.

bytes
"""""

.. code-block:: python

   __init__()                         # Create an empty bytes object. Same as b"".
   __init__(other: bytes)             # From a bytes object.
   __init__(length: u64)
   length(self) -> u64                # Its length.
   to_hex(self) -> string             # To a hexadecimal string.
   from_hex(data: string) -> bytes
   +=(self, value: bytes)             # Append bytes.
   +=(self, value: u8)                # Append a number (0 to 255).
   +(self, value: bytes) -> bytes     # Add bytes.
   +(self, value: u8) -> bytes        # Add a number (0 to 255).
   ==(self)                           # Comparisons.
   !=(self)
   <(self)
   <=(self)
   >(self)
   >=(self)
   []=(self, index: u64, value: u8)
   [](self, index: u64) -> u8
   []=(self,
       begin: u64,                    # Set subbytes.
       end: u64,
       step: u64,
       value: bytes)
   [](self,
      begin: u64,                     # Get subbytes.
      end: u64,
      step: u64) -> bytes
   __in__(self, value: u8) -> bool    # Contains value.

tuple
"""""

.. code-block:: python

   ==(self)                         # Comparisons.
   !=(self)
   <(self)
   <=(self)
   >(self)
   >=(self)
   []=(self, index: u64, item: TN)  # Set item at index. The index  must be known at
                                    # compile time.
   [](self, index: u64) -> TN       # Get item at index. The index must be known at
                                    # compile time.

list
""""

.. code-block:: python

   __init__()                      # Create an empty list. Same as [].
   __init__(other: [T])            # From a list.
   __init__(length: u64)
   length(self) -> u64             # Its length.
   +=(self, value: [T])            # Append a list.
   +=(self, value: T)              # Append an item.
   ==(self)                        # Comparisons.
   !=(self)
   <(self)
   <=(self)
   >(self)
   >=(self)
   []=(self, index: u64, item: T)
   [](self, index: u64) -> T
   []=(self,                       # Set a sublist.
       begin: u64,
       end: u64,
       step: u64,
       value: [T])
   [](self,                        # Get a sublist.
      begin: u64,
      end: u64,
      step: u64) -> [T]
   __in__(self, item: T) -> bool   # Contains item.
   sort(self)                      # Sort items in place.
   reverse(self)                   # Reverse items in place.

dict
""""

.. code-block:: python

   __init__()                     # Create an empty dictionary. Same as {}.
   __init__(other: {TK: TV})      # From a dict.
   __init__(pairs: [(TK, TV)])    # Create from a list.
   ==(self)                       # Comparisons.
   !=(self)
   []=(self, key: TK, value: TV)  # Set value for key.
   [](self, key: TK) -> TV        # Get value for key.
   |=(self, other: {TK: TV})      # Set/Update given key-value pairs.
   |(self, other: {TK: TV})       # Create a dict of self and other.
   __in__(self, key: TK) -> bool  # Contains given key.

Built-in functions
------------------

+-----------------+--------------------------+----------------------------------------------------+
| Name            | Example                  | Comment                                            |
+=================+==========================+====================================================+
| ``input()``     | ``input("> ")``          | Print prompt and read input until newline.         |
+-----------------+--------------------------+----------------------------------------------------+
| ``open()``      | ``open("path/to/file")`` | Opens given file in given mode.                    |
+-----------------+--------------------------+----------------------------------------------------+
| ``print()``     | ``print("Hi!")``         | Prints given data.                                 |
+-----------------+--------------------------+----------------------------------------------------+
| ``range()``     | ``range(10)``            | A range of numbers.                                |
+-----------------+--------------------------+----------------------------------------------------+
| ``str()``       | ``str(10)``              | Printable represenation of given object.           |
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

- `bits`_ - Basic bits operations.

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

   for i, (k, v) in {2: 5, 6: 2}:
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

Dynamic dispatch
----------------

Call function or method with matching parameter(s). Always calls the
most specialized function or method.


Interface for generics.

.. code-block:: python

   class Message:
       pass

   class Foo(Message):
       pass

   class Bar(Message):
       pass

   class Fie(Message):
       pass

   def handle(message: Foo):
       print("Handling foo.")

   def handle(message: Bar):
       print("Handling bar.")

   def handle(message: Message):
       print("Unhandled message: {message}")

   def handle_message(message: Message):
       # Calls one of the three handle functions above based on the
       # message type. Always calls the most specialized function.
       handle(message)

   def main():
       handle_message(Foo())
       handle_message(Bar())
       handle_message(Fie())

.. code-block:: text

   $ mys run
   Handling foo.
   Handling bar.
   Unhandled message: Fie()

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

- Use ``@override(T)`` to override the method from class ``T``. Useful
  if two parent classes have methods with the same name.

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

   - Remove all unused functions, methods and variables. Should remove
     test helper functions.

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

.. _bits: https://github.com/eerimoq/mys-bits

.. _log: https://github.com/eerimoq/mys-log

.. _math: https://github.com/eerimoq/mys-math

.. _random: https://github.com/eerimoq/mys-random

.. _system: https://github.com/eerimoq/mys-system

.. _time: https://github.com/eerimoq/mys-time
