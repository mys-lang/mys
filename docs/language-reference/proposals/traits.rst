Traits
------

Use ``+`` to require multiple traits.

.. code-block:: mys

   trait Foo:
       pass

   trait Bar:
       pass

   trait Fie:
       pass
                
   func foo(value: Foo + Bar + Fie) -> Bar + Fie:
       return value
