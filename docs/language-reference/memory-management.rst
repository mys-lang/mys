Memory management
-----------------

Integers and floating point numbers are allocated on the stack, passed
by value to functions and returned by value from functions, just as
any C++ program.

Strings, bytes, tuples, lists, dicts and classes are normally
allocated on the heap and managed by reference counting. Objects that
are known not to outlive a function are allocated on the stack.

.. warning::

   Stack allocations are not yet implemented.

Reference cycles are not detected and will result in memory leaks. The
programmer must manually break reference cycles by using weak
references where needed. Only class members can be weak references.

.. code-block:: mys

   class Foo:
       parent: weak[Foo?]

   func main():
       foo = Foo(None)
       foo.parent = foo

There is no garbage collector. We want deterministic applications.
