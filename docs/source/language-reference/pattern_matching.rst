Pattern matching
----------------

Use pattern matching to promote an object to its class from one of its
traits. Pattern matching can match object contents or value as
well. **Pattern matching is only partly implemented.**

.. code-block:: python

   @trait
   class Base:
       pass

   class Foo(Base):
       pass

   class Bar(Base):
       pass

   class Fie(Base):
       pass

   def handle_message(message: Base):
       # Foo() and Bar() just means these classes with any state. No
       # instance is created, just the type is checked.
       match message:
           case Foo() as foo:
               print("Handling foo.")
           case Bar() as bar:
               print("Handling bar.")
           case _:
               print(f"Unhandled message: {message}")

   def numbers(value: i64):
       match value:
           case 0:
               print("Zero integer.")
           case 5:
               print("Five integer.")

   def strings(value: string):
       match value:
           case "foo":
               print("Foo string.")
           case _:
               print("Other string.")

   def main():
       handle_message(Foo())
       handle_message(Bar())
       handle_message(Fie())
       numbers(0)
       numbers(1)
       numbers(5)
       strings("foo")
       strings("bar")

.. code-block:: text

   $ mys run
   Handling foo.
   Handling bar.
   Unhandled message: Fie()
   Zero integer.
   Five integer.
   Foo string.
   Other string.
