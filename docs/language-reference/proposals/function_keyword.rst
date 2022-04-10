Function keyword
----------------

Replace ``def`` with ``fn``, ``fun`` or ``func``. Possibly ``meth`` or
similar in classes.

Example
^^^^^^^

.. code-block:: mys

   class Foo:
       v: i64

       func __init__(self):
           self.v = 0

       fun add(self, v: i64):
           self.v += v

       meth sub(self, v: i64):
           self.v -= v

   fn main():
       add()
