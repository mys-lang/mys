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
