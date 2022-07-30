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

.. code-block:: mys

   iN(number: string,             # String to signed integer. Uses string
      base: u32 = 10)             # prefix (0x, 0o, 0b or none) if base is 0,
                                  # otherwise no prefix is allowed.
   uN(number: string,             # String to unsigned integer. Uses string
      base: u32 = 10)             # prefix (0x, 0o, 0b or none) if base is 0,
                                  # otherwise no prefix is allowed.
   iN(value: f32/f64)             # Floating point number to signed integer.
   uN(value: f32/f64)             # Floating point number to unsigned integer.
   iN(value: bool)                # Boolean to signed integer (0 or 1).
   uN(value: bool)                # Boolean to unsigned integer (0 or 1).
   i64(value: char)               # Character to signed integer.
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

.. code-block:: mys

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

.. code-block:: mys

   bool(value: iN/uN)    # Integer to boolean. 0 is false, rest true.
   bool(value: f32/f64)  # Floating point number to boolean. 0.0 is false,
                         # rest true.

char
""""

.. code-block:: mys

   char(number: i64)
   +=(value: i64)         # Add given value.
   +(value: i64) -> char  # Add given value.
   -=(value: i64)         # Subtract given value.
   -(value: i64) -> char  # Subtract given value.
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
| ``set(T)``                        | ``{5, 9}``            | A set with items of type T.                              |
+-----------------------------------+-----------------------+----------------------------------------------------------+
| ``class Name``                    | ``Name()``            | A class.                                                 |
+-----------------------------------+-----------------------+----------------------------------------------------------+

string
""""""

.. code-block:: mys

   __init__()                                # Create an empty string. Same as "".
   __init__(character: char)                 # From a character.
   __init__(other: bytes)                    # From UTF-8 bytes.
   __init__(other: string)                   # From a string.
   to_utf8(self) -> bytes                    # To UTF-8 bytes.
   length(self) -> i64                       # Length.
   +(self, value: string) -> string          # Add a string.
   +(self, value: char) -> string            # Add a character.
   ==(self)                                  # Comparisons.
   !=(self)
   <(self)
   <=(self)
   >(self)
   >=(self)
   *(self, count: u64)                       # Repeat.
   [](self, index: i64) -> char              # Get a character.
   [](self,                                  # Get a substring.
      begin: i64,
      end: i64,
      step: i64) -> string
   __in__(self, value: char) -> bool         # Contains character.
   __in__(self, value: string) -> bool       # Contains string.
   starts_with(self,                         # Return true if string starts with given substring.
               value: string) -> bool
   ends_with(self,                           # Return true if string ends with given substring.
             value: string) -> bool
   starts_with(self, value: string) -> bool  # Return true if starts with given value.
   ends_with(self, value: string) -> bool    # Return true if ends with given value.
   split(self) -> [string]                   # Split into list of strings with
                                             # \s+ as separator regex.
   split(self,                               # Split into list of strings with given
         separator: string) -> [string]      # separator string.
   split(self,                               # Split into list of strings with given
         separator: regex) -> [string]       # separator regex.
   match(self,                               # Match with regex.
         pattern: regex) -> regexmatch?
   join(self, parts: [string]) -> string     # Join given list of strings with the string
                                             # itself.
   strip(self, chars: string) -> string      # Strip leading and trailing characters.
   strip_left(self,                          # Strip leading characters.
              chars: string) -> string
   strip_right(self,                         # Strip trailing characters.
               chars: string) -> string
   lower(self) -> string                     # Make string lower case.
   upper(self) -> string                     # Make string upper case.
   capitalize(self) -> string                # Capitalize string.
   casefold(self) -> string                  # Stronger variant of lower that should be used when
                                             # doing case insensitive comparison.
   find(self,                                # Find the first occurrence of given character
        sub: char,                           # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = <length>) -> i64
   find(self,                                # Find the first occurrence of given substring
        sub: string,                         # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = <length>) -> i64
   partition(self, separator: char) ->       # Find the first occurrence of given separator. If found,
       (string, string, string)              # returns a tuple with characters before separator, the
                                             # separator itself and the characters after the separator.
   replace(self,                             # Replace old with new.
           old: char,
           new: char) -> string
   replace(self,                             # Replace old with new.
           old: string,
           new: string) -> string

bytes
"""""

.. code-block:: mys

   __init__()                               # Create an empty bytes object. Same as b"".
   __init__(other: bytes)                   # From a bytes object.
   __init__(hex: string)                    # From a hexadecimal string.
   __init__(length: u64)
   to_hex(self) -> string                   # To a hexadecimal string.
   length(self) -> i64                      # Length.
   starts_with(self, value: bytes) -> bool  # Return true if starts with given value.
   ends_with(self, value: bytes) -> bool    # Return true if ends with given value.
   find(self,                               # Find the first occurrence of given substring
        sub: bytes,                         # within given limits. Returns -1 if not found.
        start: i64 = 0,
        end: i64 = <length>) -> i64
   resize(self, size: i64)                  # Resize to given size.
   reserve(self, size: i64)                 # Reserve memory for given size.
   +=(self, value: bytes)                   # Append bytes.
   +=(self, value: u8)                      # Append a number (0 to 255).
   +(self, value: bytes) -> bytes           # Add bytes.
   +(self, value: u8) -> bytes              # Add a number (0 to 255).
   ==(self)                                 # Comparisons.
   !=(self)
   <(self)
   <=(self)
   >(self)
   >=(self)
   []=(self, index: i64, value: u8)
   [](self, index: i64) -> u8
   []=(self,
       begin: u64,                          # Set subbytes.
       end: u64,
       step: u64,
       value: bytes)
   [](self,
      begin: u64,                           # Get subbytes.
      end: u64,
      step: u64) -> bytes
   __in__(self, value: u8) -> bool          # Contains value.

tuple
"""""

.. code-block:: mys

   ==(self)                         # Comparisons.
   !=(self)
   <(self)
   <=(self)
   >(self)
   >=(self)
   []=(self, index: u64, item: TN)  # Set item at index. The index must be known at
                                    # compile time.
   [](self, index: u64) -> TN       # Get item at index. The index must be known at
                                    # compile time.

list
""""

See also :ref:`list-comprehensions`.

.. code-block:: mys

   __init__()                      # Create an empty list. Same as [].
   __init__(other: [T])            # From a list.
   __init__(values: {TK: TV})      # From a dict. Each key-value pair becomes a
                                   # tuple.
   __init__(value: string)         # From a string.
   __init__(length: u64)
   length(self) -> i64             # Length.
   ==(self)                        # Comparisons.
   !=(self)
   []=(self, index: i64, item: T)
   [](self, index: i64) -> T
   []=(self,                       # Set a sublist.
       begin: i64,
       end: i64,
       step: i64,
       value: [T])
   [](self,                        # Get a sublist.
      begin: i64,
      end: i64,
      step: i64) -> [T]
   __in__(self, item: T) -> bool   # Contains item.
   append(self, value: T)          # Append an item.
   extend(self, value: [T])        # Append a list.
   insert(self,                    # Insert an item as index.
          index: i64,
          value: [T])
   pop(index: i64 = -1) -> T       # Pop item at index.
   remove(self, item: T)           # Remove first item equal to item.
   sort(self)                      # Sort items in place.
   reverse(self)                   # Reverse items in place.
   count(self, item: T)            # Count how many times given item
                                   # is in the list.
   clear(self)                     # Clear the list.
   find(self, value: T) -> i64     # Find the first occurrence of given value.
                                   # Returns -1 if not found.

dict
""""

See also :ref:`dict-comprehensions`.

.. code-block:: mys

   __init__()                        # Create an empty dictionary. Same as {}.
   __init__(other: {TK: TV})         # From a dict.
   __init__(pairs: [(TK, TV)])       # Create from a list.
   length(self) -> i64               # Length.
   ==(self)                          # Comparisons.
   !=(self)
   []=(self, key: TK, value: TV)     # Set value for key.
   [](self, key: TK) -> TV           # Get value for key.
   |=(self, other: {TK: TV})         # Set/Update given key-value pairs.
   |(self, other: {TK: TV})          # Create a dict of self and other.
   get(self,                         # Get value for key. Return default
       key: TK,                      # if missing. Inserts default if missing
       default: TV? = None,          # and insert is True
       insert: bool = False) -> TV?
   pop(self,                         # Pop value for key. Return default
       key: TK,                      # if missing.
       default: TV? = None) -> TV?
   __in__(self, key: TK) -> bool     # Contains given key.

set
"""

.. code-block:: mys

   __init__()                        # Create an empty dictionary. Same as {}.
   length(self) -> i64               # Length.
   ==(self)                          # Comparisons.
   !=(self)
   |=(self, other: {T})              # Set/Update given items.
   add(self, item: T)                # Add given item to the set.
   remove(self, item: T)             # Remove given item from the set. Raises
                                     # KeyError is missing.
   discard(self, item: T)            # Remove given item from the set.
   pop(self) -> T                    # Remove and return an arbitrary item from
                                     # the set.
   clear(self)                       # Remove all items from the set.
   __in__(self, item: T) -> bool     # Contains given item.
