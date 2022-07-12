Traits
------

Use ``+`` to implement multiple traits.

.. code-block:: mys

   @trait
   class Foo:
       pass

   @trait
   class Bar:
       pass

   @trait
   class Fie:
       pass
                
   func foo(value: Foo + Bar + Fie) -> Bar + Fie:
       return value
