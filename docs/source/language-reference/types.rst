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
| ``string``                        | ``"Hi!"``             | A sequence of unicode characters. Immutable.             |
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
   *=(self, count: u64)                    # Repeat and replace with new string.
   [](self, index: u64) -> char            # Get a character.
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
   strip(self, chars: string)              # Strip leading and trailing characters.
   strip_left(self, chars: string)         # Strip leading characters.
   strip_right(self, chars: string)        # Strip trailing characters.
   lower(self)                             # Make string lower case.
   upper(self)                             # Make string upper case.
   capitalize(self)                        # Capitalize string.
   casefold(self)                          # Stronger variant of lower that
                                           # should be used when doing case insensitive comparison.
   find(self,                              # Find the first occurrence of given character
        sub: char,                         # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = <length>) -> i64
   find(self,                              # Find the first occurrence of given substring
        sub: string,                       # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = <length>) -> i64
   partition(self,                         # Find the first occurrence of given separator.
       separator: char)
       -> (string, string, string)         # If found, returns a tuple with characters before separator,
                                           # the separator itself and the characters after the separator.
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

See also :ref:`list-comprehensions`.

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

See also :ref:`dict-comprehensions`.

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

