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

Reference cycles are not detected and will result in memory leaks. The
plan is to make the programmer manually break reference cycles by
defining members as ``weak``.

.. warning::

   Weak references are not yet implemented.

Here is an example that uses ``weak`` to break reference cycles in a
doubly linked list. All three nodes in the list are freed when
``create_and_print_list()`` returns.

.. code-block:: python

   class Node:
       prev: weak[Node]
       next: Node

   def create_list() -> Node:
       head = Node(None, None)
       tail = Node(None, None)
       middle = Node(head, tail)
       head.next = middle
       tail.prev = middle

       return head

   def create_and_print_list():
       print(create_list())

   def main():
       create_and_print_list()

There is no garbage collector. We want deterministic applications.

.. _C++ shared pointers: https://en.cppreference.com/w/cpp/memory/shared_ptr
