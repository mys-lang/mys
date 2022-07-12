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
programmer must manually break reference cycles by assigning ``None``
to them.

Here is an example of how to break reference cycles.

.. code-block:: mys

   class Foo:
       foo: Foo

   func main():
       # foo_1 -> foo_2 -> foo_1 -> ..., which would result in both objects
       # leaking.
       foo_1 = Foo(None)
       foo_2 = Foo(foo_1)
       foo_1.foo = foo_2

       # Once the objects are not needed anymore, we must set at least one of
       # the foo members to None to break the reference cycle.
       # We end up with foo_2 -> foo_1 -> None, which has no reference cycles.
       foo_1.foo = None

There is no garbage collector. We want deterministic applications.
