|discord|_

WARNING
=======

Mys is still in the very early stages of development. API:s will
change, so now is the time to make suggestions! Join the `Mys Discord
server`_ to get in touch with the developers!

🐁 Mys
======

The Mys (/maɪs/) programming language - an attempt to create a
statically typed Python-like language that produces fast binaries.

Mys is heavily inspired by Python's syntax and Rust's packaging.

Source code:

.. code-block:: python

   from random.pseudo import random

   def main():
       print(random())

Package configuration:

.. code-block:: toml

   [package]
   name = "robot"
   version = "0.1.0"
   authors = ["Mys Lang <mys.lang@example.com>"]

   [dependencies]
   random = "*"

Mys is mainly targeting resource constrained single and multi core
embedded systems, but is just as useful in desktop environments.

Notable differences to Python:

- Traits instead of classic inheritence.

- Statically typed.

- Bytes and strings are mutable.

- Integers are bound (i32, u32, i64, ...).

- Iterators/generators do not (yet?) exist.

- Rust-like generic functions and classes.

- Only packages. No stand alone modules.

- Compiled to machine code. No interpreter.

- Data races and memory corruption possible, but unlikely.

- No async.

- Only ``from ... import ...`` is allowed. ``import ...`` is not.

- Only functions, enums, traits, classes and variables can be
  imported, not modules.

Tutorial
--------

If you havn't already installed Mys, install it as described in the
`Installation`_ section.

Now, create a package called ``foo`` with the command ``mys new foo``,
and then enter it. This package is used in throughout the tutorial.

.. image:: https://github.com/mys-lang/mys/raw/main/docs/new.png

``src/main.mys`` implements the hello world application.

.. code-block:: python

   def main():
       print("Hello, world!")

Build and run the application with the command ``mys run``. It prints
``Hello, world!``, just as expected.

.. image:: https://github.com/mys-lang/mys/raw/main/docs/run.png

``src/lib.mys`` implements the function ``add()`` and it's test
``test_add()``. This examplifies how to test your Mys modules.

.. code-block:: python

   def add(first: i32, second: i32) -> i32:
       return first + second

   @test
   def test_add():
       assert add(1, 2) == 3

Build and run the tests with the command ``mys test``.

.. image:: https://github.com/mys-lang/mys/raw/main/docs/test.png

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

.. image:: https://github.com/mys-lang/mys/raw/main/docs/run-universe.png

Replace the code in ``src/main.mys`` with the code below. It
examplifies how to use functions, classes, errors, types and command
line arguments. The syntax is almost identical to Python, so many
readers should easily understand it.

.. code-block:: python

   def func_1(a: i64) -> (i64, string):
       if a == 5:
           text = "Foo"
       else:
           text = "Bar"

       return 2 * a, text

   def func_2(a: i64, b: i64) -> i64:
       for i in range(b):
           a += i * b

       return a

   def func_3(a: i64) -> {i64: [f64]}:
       return {
           1: [2.0],
           10 * a: [7.5, -1.0]
       }

   def func_4():
       try:
           raise GeneralError()
       except:
           print("func_4():      An error occurred.")

   def func_5() -> [i64]:
       small: [i64] = []

       for v in [3, 1, 5, 7, 2]:
           if v < 5:
               small.append(v)

       small.sort()
       small.reverse()

       return small

   class Calc:
       value: i64

       def triple(self):
           self.value *= 3

   def main(argv: [string]):
       value = i64(argv[1])
       print("func_1(value):", func_1(value))
       print("func_2(value):", func_2(value, 1))
       print("func_3(value):", func_3(value))
       func_4()
       print("func_5():     ", func_5())
       calc = Calc(value)
       calc.triple()
       print("calc:         ", calc)

Build and run it.

.. code-block::

   $ mys run 5
   func_1(value): (10, "Foo")
   func_2(value): 5
   func_3(value): {1: [2], 50: [7.5, -1]}
   func_4():      An error occurred.
   func_5():      [3, 2, 1]
   calc:          Calc(value=15)

Installation
------------

Linux
^^^^^

Install Python 3.8 or later, and then install Mys using ``pip``.

.. code-block:: python

   $ pip install mys

You must also have recent versions of ``g++``, ``make`` and ``pylint``
installed. Optionally install ``ccache`` for potentially faster
builds.

Windows
^^^^^^^

#. Install `Cygwin`_. Required packages are ``gcc-g++``, ``make``,
   ``python38`` and ``python38-devel``. Optionally select ``ccache``
   as well for potentially faster builds.

#. Start Cygwin and install ``pip`` and Mys.

   .. code-block:: text

      $ /usr/bin/python3.8 -m easy_install pip
      $ /usr/bin/python3.8 -m pip mys

Loops
-----

``while`` and ``for`` loops are available.

``while`` loops run until given condition is false or until
``break``.

``for`` loops can only iterate over ranges, lists, dictionaries,
strings and bytes. All but dictionaries supports combinations of
``enumerate()``, ``slice()``, ``reversed()`` and ``zip()``. Never
modify variables you are iterating over, or the program may crash!

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

   for i, v in enumerate(range(10, 4, -2)):
       pass

   # Lists.
   for v in [3, 1]:
       pass

   for i, v in enumerate([3, 1]):
       pass

   for v, s in zip([3, 1], ["a", "c"]):
       pass

   for v in slice([3, 1, 4, 2], 1, -1):
       pass

   for v in reversed([3, 1, 4, 2]):
       pass

   # Dictionaries.
   for k, v in {2: 5, 6: 2}:
       pass

   # Strings. 'c' is char.
   for c in "foo":
       pass

   for i, c in enumerate("foo"):
       pass

   # Bytes. 'b' is u8.
   for b in b"\x03\x78":
       pass

   for i, b in enumerate(b"\x03\x78"):
       pass

Pattern matching
----------------

Use pattern matching to promote an object to its class from one of its
traits. Pattern matching can match object contents or value as well.

.. code-block:: python

   @trait
   class Base:
       pass

   class Foo(Base):
       pass

   class Bar(Base):
       pass

   class Fie(Base):
       pass

   def handle_message(message: Base):
       # Foo() and Bar() just means these classes with any state. No
       # instance is created, just the type is checked.
       match message:
           case Foo() as foo:
               print("Handling foo.")
           case Bar() as bar:
               print("Handling bar.")
           case _:
               print(f"Unhandled message: {message}")

   def numbers(value: i64):
       match value:
           case 0:
               print("Zero integer.")
           case 5:
               print("Five integer.")

   def strings(value: string):
       match value:
           case "foo":
               print("Foo string.")
           case _:
               print("Other string.")

   def main():
       handle_message(Foo())
       handle_message(Bar())
       handle_message(Fie())
       numbers(0)
       numbers(1)
       numbers(5)
       strings("foo")
       strings("bar")

.. code-block:: text

   $ mys run
   Handling foo.
   Handling bar.
   Unhandled message: Fie()
   Zero integer.
   Five integer.
   Foo string.
   Other string.

Generics
--------

.. code-block:: python

   @generic(T1, T2)
   class Foo:
       a: T1
       b: T2

   # Type alias.
   Bar = Foo[i32, string]

   @generic(T)
   def fie(v: T) -> T:
       return v

   def main():
       print(Foo[bool, u8](True, 100))
       print(Foo("Hello!", 5))
       print(Bar(-5, "Yo"))

       print(fie[u8](2))
       print(fie(1))

.. code-block:: text

   $ mys run
   Foo(a: True, b: 100)
   Foo(a: "Hello!", b: 5)
   Bar(a: -5, b: "Yo")
   2
   1

Classes and traits
------------------

- Instance members are accessed with ``<object>.<variable/method>``.

- Implemented trait methods may be decorated with ``@trait(T)``.

- Automatically added methods (``__init__()``, ``__str__()``, ...)
  are only added if missing.

- Decorate with ``@trait`` to make a class a trait.

  ToDo: Introduce the trait keyword.

- There is no traditional OOP inheritance. Traits are used instead.

- Traits does not have a state and cannot be instantiated.

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
       f1 = Foo(0)
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

Enumerations
------------

Enumerations are integers with named values, similar to C.

ToDo: Introduce the enum keyword.

.. code-block:: python

   @enum
   class Color:
       Red
       Green
       Blue

   @enum(u8)
   class City:
       Linkoping = 5
       Norrkoping
       Vaxjo = 10

   def main():
       assert Color(0) == Color.Red

       # Color(3) raises ValueError since 3 is not a color.

Function and method overloading
-------------------------------

Functions and methods can be overloaded.

Calls the first defined function that matches given parameter and
return value types.

.. code-block:: python

   # func 1
   def neg(v: i16) -> i16:
       return -v

   # func 2
   def neg(v: i8) -> i8:
       return -v

   # func 3
   def neg(v: i8) -> i16:
       return -v

   def main():
       v1 = neg(-5)  # Calls func 1.
       v2 = neg(i8(-5))  # Calls func 2.
       v3: i8 = neg(-5)  # Calls func 2.
       v4: i16 = neg(i8(-5))  # Calls func 3.
       v5: i8 = neg(i16(-5))  # Error. No matching function.

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

   iN(number: string, base: u32)  # String to signed integer. Uses string
                                  # prefix (0x, 0o, 0b or none) if base is 0,
                                  # otherwise no prefix is allowed.
   uN(number: string, base: u32)  # String to unsigned integer. Uses string
                                  # prefix (0x, 0o, 0b or none) if base is 0,
                                  # otherwise no prefix is allowed.
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

   fN(number: string)  # String to floating point number.
   fN(value: iN/uN)    # Integer to floating point number.
   fN(value: bool)     # Boolean to floating point number (0 or 1).
   ==                  # Comparisons.
   !=
   <
   <=
   >
   >=
   +                   # Add.
   -                   # Subtract.
   *                   # Multiply.
   /                   # Divide.
   +=                  # Add in place.
   -=                  # Subtract in place.
   *=                  # Multiply in place.
   /=                  # Divide in place.

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
   +=(value: i32)         # Add given value.
   +(value: i32) -> char  # Add given value.
   -=(value: i32)         # Subtract given value.
   -(value: i32) -> char  # Subtract given value.
   ==                     # Comparisons.
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
   to_utf8(self) -> bytes                  # To UTF-8 bytes.
   from_utf8(utf8: bytes) -> string
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
       begin: i64,
       end: i64,
       step: 64,
       value: string)
   [](self,                                # Get a substring.
      begin: i64,
      end: i64,
      step: i64) -> string
   __in__(self, value: char) -> bool       # Contains character.
   __in__(self, value: string) -> bool     # Contains string.
   starts_with(self,                       # Return true if string starts with given substring.
               substring: string) -> bool
   split(self,                             # Split into list of strings with given
         separator: string) -> [string]    # separator string.
   join(self, parts: [string]) -> string   # Join given list of strings with the string
                                           # itself.
   strip(self, chars: string)              # Strip leading and trailing characters in place.
   lstrip(self, chars: string)             # Strip leading characters in place.
   rstrip(self, chars: string)             # Strip trailing characters in place.
   lower(self)                             # Make string lower case in place.
   upper(self)                             # Make string upper case in place.
   casefold(self)                          # Stronger variant of lower that
                                           # should be used when doing case insensitive comparison.
   to_lower(self) -> string                # Return a new lower case string.
   to_upper(self) -> string                # Return a new upper case string.
   to_casefold(self) -> string             # Return a new case folded string.
   find(self,                              # Find the first occurrence of given character
        sub: char,                         # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = <length>) -> i64
   find(self,                              # Find the first occurrence of given substring
        sub: string,                       # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = <length>) -> i64
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
   __init__(values: {TK: TV})      # From a dict. Each key-value pair becomes a
                                   # tuple.
   __init__(length: u64)
   +=(self, value: [T])            # Append a list.
   +=(self, value: T)              # Append an item.
   ==(self)                        # Comparisons.
   !=(self)
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

   __init__()                        # Create an empty dictionary. Same as {}.
   __init__(other: {TK: TV})         # From a dict.
   __init__(pairs: [(TK, TV)])       # Create from a list.
   ==(self)                          # Comparisons.
   !=(self)
   []=(self, key: TK, value: TV)     # Set value for key.
   [](self, key: TK) -> TV           # Get value for key.
   |=(self, other: {TK: TV})         # Set/Update given key-value pairs.
   |(self, other: {TK: TV})          # Create a dict of self and other.
   get(key: TK, default: TV = None)  # Get value for key. Return default if missing.
   __in__(self, key: TK) -> bool     # Contains given key.

Built-in functions
------------------

+-----------------+-----------------------------+------------------------------------------------------+
| Name            | Example                     | Comment                                              |
+=================+=============================+======================================================+
| ``enumerate()`` | ``enumerate([3, -1])``      | Enumerate given iterable. Only allowed in for loops. |
+-----------------+-----------------------------+------------------------------------------------------+
| ``input()``     | ``input("> ")``             | Print prompt and read input until newline.           |
+-----------------+-----------------------------+------------------------------------------------------+
| ``len()``       | ``len("hi")``               | Get the length of given object.                      |
+-----------------+-----------------------------+------------------------------------------------------+
| ``open()``      | ``open("path/to/file")``    | Opens given file in given mode.                      |
+-----------------+-----------------------------+------------------------------------------------------+
| ``print()``     | ``print("Hi!")``            | Prints given data.                                   |
+-----------------+-----------------------------+------------------------------------------------------+
| ``range()``     | ``range(10)``               | A range of numbers. Only allowed in for loops.       |
+-----------------+-----------------------------+------------------------------------------------------+
| ``reversed()``  | ``reversed([2, 1])``        | Yield items in reversed order. Only allowed in for   |
|                 |                             | loops.                                               |
+-----------------+-----------------------------+------------------------------------------------------+
| ``slice()``     | ``slice([1, 3, 2], 1, -1)`` | A slice. Only allowed in for loops.                  |
+-----------------+-----------------------------+------------------------------------------------------+
| ``str()``       | ``str(10)``                 | Printable represenation of given object.             |
+-----------------+-----------------------------+------------------------------------------------------+
| ``zip()``       | ``zip([3, 5], ["a", "g"])`` | Yield one item from each iterable. Only allowed      |
|                 |                             | in for loops.                                        |
+-----------------+-----------------------------+------------------------------------------------------+

Special symbols
---------------

.. code-block:: text

   __file__        The module file path as a string.
   __line__        The module file line as an i64.
   __name__        The module name (including package) as a string.
   __unique_id__   A unique 64 bits integer.

Errors
------

All error names ends with ``Error`` to distinguish them from other
classes. All errors must implement the ``Error`` trait.

.. code-block:: text

   +-- GeneralError
   +-- UnreachableError
   +-- NotImplementedError
   +-- KeyError
   +-- ValueError
   +-- FileNotFoundError
   +-- NoneError
   +-- SystemExitError

Functions and methods must declare which errors they may raise.

.. code-block:: python

   @raises(TypeError)
   def foo():
       raise TypeError()

   @raises(GeneralError, TypeError)  # As foo() may raise TypeError.
   def bar(value: i32):
       match value:
           case 1:
               raise GeneralError()
           case 2:
               foo()
           case 3:
               try:
                   raise ValueError()
               except ValueError:
                   pass

Assertions
----------

Use the assert keyword to check that given condition is true.

.. code-block:: python

   assert True
   assert 1 != 5
   assert 1 in [1, 3]
   v = 1
   assert v == 2

The ``AssertionError`` error is raised if the condition is not true.

.. code-block:: text

   AssertionError: 1 == 2 is not true

Assertions are always compiled into test and debug binaries, but not
by default into optimized application binaries.

Numeric literals
----------------

There are no numeric literal suffixes. Its type is always deduced from
its context.

In inferred variable type assignments the numeric literals are their
base type. Integers are ``i64`` and floats are ``f64``.

.. code-block:: python

   def main():
       a = 1  # 1 is i64
       b = 1.0  # 1.0 is f64

Comparisions and arithmetics makes numeric literals the same type as
the other value's type.

.. code-block:: python

   def main():
       a: u64 = 1  # 1 is u64
       b: u8 = 1 + 1  # 1 and 1 are u8
       c = u8(1 + 1)  # 1 and 1 are u8
       d = u8(1 + i16(-1))  # 1 and -1 are i16

       if a == 2:  # 2 is u64
           pass

       if (1 + 3) * a == 8:  # 1, 3 and 8 are u64
           pass

       if (1 + 3) * 2 == 8:  # 1, 3, 2 and 8 are i64
           pass

       if u8(1 + 3) == 8:  # 1, 3 and 8 are u8
           pass

Passing numeric literals to functions makes them the same type as the
parameter types. First defined matching function is called.

.. code-block:: python

   def foo(a: i16, b: f32):
       pass

   # bar 1
   def bar(a: u8) -> i16:
       return i16(a)

   # bar 2
   def bar(a: u16) -> i32:
       return i32(a)

   def main():
       foo(-44, 3.2)  # -44 is i16 and 3.2 is f32

       if bar(1 + 3) == 8:  # 1 and 3 are u8 and 8 is i16 (bar 1)
           pass

       if bar(1 + u16(3)) == 8:  # 1 and 3 are u16 and 8 is i32 (bar 2)
           pass

       if bar(1 + 3) == i32(8):  # 1 and 3 are u16 and 8 is i32 (bar 2)
           pass

Global variables
----------------

Their types can't be inferred (for now).

Their names must be upper case snake case.

Initialized in import order starting from the first import in
``main.mys``. Circular dependencies between variables during
initialization is not allowed.

Given the code below, the global variables are initialized in this
order:

#. ``B = -2`` (from bar.mys)

#. ``Z = 5`` (from bar.mys)

#. ``C = 99`` (from fie.mys)

#. ``Y = 2 * Z`` (from foo.mys)

#. ``A = -1`` (from foo.mys)

#. ``X = Y + 5`` (from main.mys)

main.mys:

.. code-block:: python

   from .foo import Y

   X: i32 = Y + 5

   def main():
       print(X)

foo.mys:

.. code-block:: python

   from .bar import Z
   from .fie import C

   Y: i32 = 2 * Z
   A: i32 = C

bar.mys:

.. code-block:: python

   B: i32 = -2
   Z: i32 = 5

fie.mys:

.. code-block:: python

   C: i32 = 99

Type conversions
----------------

Implicit type conversions are only supported for numeric literals and
traits.

Extending Mys with C++
----------------------

Extending Mys with C++ is extremly easy and flexible. Strings that
starts with ``mys-embedded-c++`` are inserted at the same location in
the generated code.

.. code-block:: python

   def main():
       a: i32 = 0
       b: i32 = 0

       """mys-embedded-c++

       b = 2;
       a++;
       """

       print("a + b:", a + b)

Packages
--------

A package contains modules that other packages can import from. Most
packages contains a file called ``lib.mys``, which is imported from
with ``from <package> import <function/class/variable>``.

Packages that contains ``src/main.mys`` produces executables when
built. Such packages may also be imported from by other packages, in
which case ``src/main.mys`` is ignored.

A package:

.. code-block:: text

   my-package/
   ├── LICENSE
   ├── package.toml
   ├── pylintrc
   ├── README.rst
   └── src/
       ├── lib.mys
       └── main.mys         # Only part of packages that can build executables.

The mys command line interface:

.. code-block:: text

   mys new      Create a new package.
   mys build    Build the appliaction.
   mys run      Build and run the application.
   mys test     Build and run tests.
   mys clean    Remove build output.
   mys lint     Perform static code analysis.
   mys publish  Publish a release.
   mys install  Install an application from local package or registry.

Importing functions, enums, traits, classes and variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import functions, enums, traits, classes and variables from modules in
other packages with ``from <module> import <name>``.

Import functions, enums, traits, classes and variables from modules in
current package with ``from .<module> import <name>``. One ``.`` per
directory level.

Use ``from <module> import <name> as <new-name>`` to use a custom name.

- Imports are private. They cannot be exported.

- Circular imports are allowed.

- A module is private if its name or any directory in its path starts
  with an underscore.

- A private module can only be imported from by other modules in the
  same package.

- All public definitions in a private module can only be used by other
  modules in the same package.

- Imports from modules within the same package must be relative.

Here are a few examples:

.. code-block:: python

   from mypkg1 import func1                   # Imports from mypkg1/src/lib.mys.
   from mypkg2.subpkg1.mod1 import func2 as func3
   from mypkg2 import Class1
   from mypkg2 import var1
   from ..mod1 import func4                   # Imports from ../mod1.mys.
   from ...subpkg2.mod1 import func5          # Imports from ../../subpkg2/mod1.mys.
   from . import func6                        # Imports from lib.mys in the same
                                              # folder.
   # from mypkg2._mod1 import func7           # Not allowed as _mod1 is private.
   # from mypkg2._subpkg1.mod1 import func8   # Not allowed as _subpkg1 and all its
                                              # content is private.
   from ._mod1 import func7                   # Imports from private _mod1.mys.
   from ._subpkg1.mod1 import func8           # Imports from private _subpkg1/mod1.mys.

   def foo():
       func1()
       func3()
       Class1()
       print(var1)
       func4()
       func5()
       func6()

List of packages
^^^^^^^^^^^^^^^^

Some works, some does not even compile. Big work in progress!

- `argparse`_ - Command line argument parser.

- `base64`_ - Base64 encoding and decoding.

- `bits`_ - Basic bits operations.

- `json`_ - JSON encoding and decoding.

- `log`_ - Logging facilities.

- `math`_ - Basic math operations.

- `random`_ - Random numbers.

- `sqlite`_ - SQLite.

- `system`_ - System services.

- `time`_ - Date and time.

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

``--no-ccache``: Do not use `Ccache`_.

Mys tool configuration
----------------------

The mys command line tool can be configured to fit your development
environment.

NOTE: It's currently not possible to configure anything.

Search order:

#. The environment variable ``MYS_CONFIG``.

#. The file ``~/.config/mys/config.toml``

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

#. Compile the C++ code with ``g++``.

#. Link the application with ``g++``.

Calling mys from GNU Make recipe
--------------------------------

``mys`` uses ``make`` internally. Always prepend the command with
``+`` to share jobserver.

Contributing
------------

It's usually a good idea to add a test in ``tests/files/<name>.mys``
and execute with ``make test -j 8 ARGS="-k <pattern>``.

Add positive and negative tests in `tests/test_mys.py`_.

Build and run all tests in parallel with ``make test-parallel -j 8``.

Build and run all tests in parallel and all examples with ``make -j 8``.

Open ``htmlcov/index.html`` for code coverage.

Development environments
^^^^^^^^^^^^^^^^^^^^^^^^

Ubuntu
""""""

Install tools, clone the repo and run tests and examples.

.. code-block:: text

   $ sudo apt install git g++ make pylint ccache
   $ git clone ssh://git@github.com/mys-lang/mys
   $ python -m pip install -r mys/requirements.txt
   $ python -m pip install coverage pylint
   $ cd mys
   $ make

Windows
"""""""

The Mys project is built in Cygwin.

#. Install `Cygwin`_. Required packages are ``gcc-g++``, ``make``,
   ``python38``, ``ccache``, ``git`` and ``python38-devel``.

#. Start Cygwin and do the following one time setup.

   .. code-block:: text

      $ ln -s /usr/bin/python3.8 /usr/bin/python
      $ python -m easy_install pip
      $ git clone ssh://git@github.com/mys-lang/mys
      $ python -m pip install -r mys/requirements.txt
      $ python -m pip install coverage pylint

#. Run tests and examples.

   .. code-block:: text

      $ cd mys
      $ export PYTHONUTF8=1  # Probably needed.
      $ make

Mocking
-------

.. code-block:: python

   from random.pseudo import random

   def add(value: f64) -> f64:
       return value + random()

   def test_add():
       random_mock_once(5.3)
       assert add(1.0) == 6.3

.. |discord| image:: https://img.shields.io/discord/777073391320170507?label=Discord&logo=discord&logoColor=white
.. _discord: https://discord.gg/GFDN7JvWKS

.. _Mys Discord server: https://discord.gg/GFDN7JvWKS

.. _Cygwin: https://www.cygwin.com/

.. _official Visual Code guide: https://code.visualstudio.com/docs/languages/overview#_adding-a-file-extension-to-a-language

.. _C++ shared pointers: https://en.cppreference.com/w/cpp/memory/shared_ptr

.. _examples: https://github.com/mys-lang/mys/tree/main/examples

.. _tests: https://github.com/mys-lang/mys/tree/main/tests/files

.. _Fibonacci example: https://github.com/mys-lang/mys/blob/main/examples/fibonacci/src/main.mys

.. _bar package: https://github.com/mys-lang/mys-bar

.. _examples/wip/message_passing: https://github.com/mys-lang/mys/tree/main/examples/wip/message_passing

.. _argparse: https://github.com/mys-lang/mys-argparse

.. _base64: https://github.com/mys-lang/mys-base64

.. _bits: https://github.com/mys-lang/mys-bits

.. _json: https://github.com/mys-lang/mys-json

.. _log: https://github.com/mys-lang/mys-log

.. _math: https://github.com/mys-lang/mys-math

.. _random: https://github.com/mys-lang/mys-random

.. _sqlite: https://github.com/mys-lang/mys-sqlite

.. _system: https://github.com/mys-lang/mys-system

.. _time: https://github.com/mys-lang/mys-time

.. _tests/files/various.mys: https://github.com/mys-lang/mys/blob/main/tests/files/various.mys

.. _tests/test_mys.py: https://github.com/mys-lang/mys/blob/main/tests/test_mys.py

.. _Ccache: https://ccache.dev/
