Traits
------

Use ``+`` to require multiple traits.

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
                
   def foo(value: Foo + Bar + Fie) -> Bar + Fie:
       return value
