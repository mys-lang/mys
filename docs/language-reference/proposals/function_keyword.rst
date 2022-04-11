Function keyword
----------------

Replace ``def`` with ``fun``.

Example
^^^^^^^

.. code-block:: mys

   class Foo:
       v: i64

       fun __init__(self):
           self.v = 0

       fun add(self, v: i64):
           self.v += v

       fun sub(self, v: i64):
           self.v -= v

   fun main():
       add()
