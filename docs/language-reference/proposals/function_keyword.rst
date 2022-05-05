Func and test keywords
----------------------

Replace ``def`` with ``func`` and ``test``.

Test functions have their own namespace and can only be called by the
test framework.

Example
^^^^^^^

.. code-block:: mys

   class Foo:
       v: i64

       func __init__(self):
           self.v = 0

       func add(self, v: i64):
           self.v += v

       func sub(self, v: i64):
           self.v -= v

   func main():
       foo = Foo()
       foo.add(1)
       print(foo.v)

   test foo():
       foo = Foo()
       foo.add(1)
       assert foo.v == 1
