|buildstatus|_
|coverage|_

🐁 Mys
======

The Mys (/maɪs/) programming language - an attempt to create a
statically typed Python-like language that produces fast binaries.

Mys is heavily inspired by Python's syntax and Rust's packaging.

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

Installation
------------

Install Python 3.6 or later, and then install Mys using ``pip``.

.. code-block:: python

   $ pip install mys

You must also have a recent versions of ``g++``, ``make`` and
``pylint`` installed.

Tutorial
--------

First of all, create a package called ``foo`` with the command ``mys
new foo``, and then enter it. This package is used in throughout the
tutorial.

.. image:: https://github.com/eerimoq/mys/raw/master/docs/new.png

``src/main.mys`` implements the hello world application. This file is
only be part of application packages (executables).

.. code-block:: python

   def main():
       print('Hello, world!')

Build and run the application with the command ``mys run``. It prints
``Hello, world!``, just as expected.

.. image:: https://github.com/eerimoq/mys/raw/master/docs/run.png

``src/lib.mys`` implements ``add()`` and it's test
``test_add()``. This file is normally part of both application
packages and plain library packages.

.. code-block:: python

   def add(first: int, second: int) -> int:
       return first + second

   @test
   def test_add():
       assert_eq(add(1, 2), 3)

Build and run the tests with the command ``mys test``.

.. image:: https://github.com/eerimoq/mys/raw/master/docs/test.png

Replace the code in ``src/main.mys`` with the code below. It
examplifies how to use functions, classes, exceptions, types and
command line arguments. The syntax is almost identical to Python, so
most readers should easily understand it.

**NOTE**: This code does not yet work. This is just an example of what
an application could look like in the future. The `Fibonacci example`_
works, so try that instead!

.. code-block:: python

   def func_1(a: int) -> (int, Final[str]):
       return 2 * a, 'Bar'

   def func_2(a: int, b: int = 1) -> int:
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

Print package statistics with ``mys stats``.

.. code-block:: text

   $ mys stats
   Files:    2
   Blank:    3
   Comments: 0
   Code:     5

Built-in functions and classes
------------------------------

+----------------------------------------------------------------------------------------+
| Built-in functions and classes                                                         |
+=================+=================+=================+=================+================+
| ``abs()``       | ``all()``       | ``any()``       | ``bool()``      | ``bytes()``    |
+-----------------+-----------------+-----------------+-----------------+----------------+
| ``chr()``       | ``dict()``      | ``enumerate()`` | ``float()``     | ``format()``   |
+-----------------+-----------------+-----------------+-----------------+----------------+
| ``int()``       | ``len()``       | ``list()``      | ``max()``       | ``min()``      |
+-----------------+-----------------+-----------------+-----------------+----------------+
| ``open()``      | ``ord()``       | ``print()``     | ``range()``     | ``reversed()`` |
+-----------------+-----------------+-----------------+-----------------+----------------+
| ``round()``     | ``str()``       | ``sum()``       | ``tuple()``     | ``zip()``      |
+-----------------+-----------------+-----------------+-----------------+----------------+

All built-ins aims to behave like their Python counterparts, with the
following differences.

- ``abs()`` only supports integer and floating point numbers.

- ``all()`` and ``any()`` only supports lists of ``bool()``.

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
| ``float``                         | ``5.5``, ``-100.0``   | A floating point number. Usually 32 bits.                |
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

Packages
--------

A package contains modules that other packages can use. All packages
contains a file called ``lib.mys``, which is imported with ``import
<package>``.

There are two kinds of packages; library packages and application
packages. The only difference is that application packages contains a
file called ``src/main.mys``, which contains the application entry
point ``def main(...)``. Application packages produces an executable
when built (``mys build``), libraries does not.

A package:

.. code-block:: text

   my-package/
   ├── Package.toml
   ├── pylintrc
   ├── README.rst
   ├── src/
   │   ├── lib.mys
   │   └── main.mys         # Only part of application packages.
   └── tst/
       └── test_lib.mys

The mys command line interface:

.. code-block:: text

   mys new      Create a new package.
   mys build    Build the appliaction.
   mys run      Build and run the application.
   mys clean    Remove build output.
   mys lint     Perform static code analysis.
   mys test     Build and run tests.
   mys publish  Publish a release.

Importing modules
^^^^^^^^^^^^^^^^^

- Import the special ``lib``-module with ``import <package>``.

- Import a module with ``import <package>[.<sub-package>]*.<module>``.

- Import selected functions and classes with ``from
  <package>[.<sub-package>]*[.<module>] import <function/class>``.

Use ``import ... as <name>`` to use a custom name.

Here are a few examples:

.. code-block:: python

   import mypkg1  # Imports mypkg1.lib.
   import mypkg2.mod1
   import mypkg2.subpkg1.mod1 as mod1
   from mypkg3.subpkg1.mod1 import func1
   from mypkg3.subpkg1.mod1 import func2 as func3

   def foo():
       mypkg1.func()
       mypkg2.mod1.func()
       mod1.func()
       func1()
       func3()

Extending Mys with C++
----------------------

Extending Mys with C++ is extremly easy and flexible. Strings that
starts with ``mys-embedded-c++`` are inserted at the same location in
the generated code.

.. code-block:: python

   def main():
       a: int = 0

       '''mys-embedded-c++

       int b = 2;
       a++;
       '''

       print('a + b:', a + b)

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

- Lambda functions are not supported.

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

Notebook for the developer
--------------------------

Importing ideas:

.. code-block:: c++

   // from mypkg4 import func2
   // def foo():
   //     func2()
   #include "mypkg4/lib.mys.hpp"
   void foo() {
       mypkg4::lib::func2();
   }

   constexpr auto func2 = [] (auto &&...args) {
       return mypkg4::func2(std::forward<decltype(args)>(args)...);
   };

   // Function alias when using import ... as <name>.
   constexpr auto bar = [] (auto &&...args) {
       return foo(std::forward<decltype(args)>(args)...);
   };

   // Class alias when using import ... as <name>.
   typedef <package>::<module>::MyClass <name>;

Mocking ideas:

.. code-block:: python

   def my_add(a: int, b: int) -> int:
       assert_eq(a, 1)
       assert_eq(b, 2)

       return -1

   def test_add():
       'mys-mock-once {package_name}.add = my_add'
       assert_eq({package_name}.add(1, 2), -1)

.. |buildstatus| image:: https://travis-ci.com/eerimoq/mys.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/mys

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/mys/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/mys

.. _official Visual Code guide: https://code.visualstudio.com/docs/languages/overview#_adding-a-file-extension-to-a-language

.. _C++ shared pointers: https://en.cppreference.com/w/cpp/memory/shared_ptr

.. _examples: https://github.com/eerimoq/mys/tree/master/examples

.. _tests: https://github.com/eerimoq/mys/tree/master/tests/files

.. _Fibonacci example: https://github.com/eerimoq/mys/blob/master/examples/fibonacci/src/main.mys
