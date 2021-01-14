Memory management
-----------------

Integers and floating point numbers are allocated on the stack, passed
by value to functions and returned by value from functions, just as
any C++ program.

Strings, bytes, tuples, lists, dicts and classes are normally
allocated on the heap and managed by `C++ shared pointers`_. Objects
that are known not to outlive a function are allocated on the
stack.

.. warning::

   Stack allocations are not yet implemented.

Reference cycles are not detected and will result in memory leaks.

There is no garbage collector.

.. _C++ shared pointers: https://en.cppreference.com/w/cpp/memory/shared_ptr
