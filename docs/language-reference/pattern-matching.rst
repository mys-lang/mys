Pattern matching
----------------

Use pattern matching to promote an object to its class from one of its
traits. Pattern matching can match object contents or value as
well.

.. warning::

   Pattern matching is only partly implemented.

Below is the contents of ``src/main.mys`` found in the
`pattern_matching example`_.

.. code-block:: mys

   trait Base:
       pass

   class Foo(Base):
       a: i64
       b: string

   class Bar(Base):
       pass

   class Fie(Base):
       pass

   func classes(base: Base):
       # Foo() and Bar() just means these classes with any state. No
       # instance is created, just the type is checked.
       match base:
           case Foo(a=1) as foo:
               print(f"Class Foo with a=1 and b=\"{foo.b}\".")
           case Foo(a=2, b="ho"):
               print("Class Foo with a=2 and b=\"ho\".")
           case Foo():
               print("Class Foo.")
           case Bar():
               print("Class Bar.")
           case _:
               print(f"Other class: {base}")

   func numbers(value: i64):
       match value:
           case 0:
               print("Zero integer.")
           case 5:
               print("Five integer.")

   func strings(value: string):
       match value:
           case "foo":
               print("String foo.")
           case _:
               print(f"Other string: {value}")

   func main():
       classes(Foo(1, "hi"))
       classes(Foo(2, "ho"))
       classes(Foo(3, ""))
       classes(Bar())
       classes(Fie())
       numbers(0)
       numbers(1)
       numbers(5)
       strings("foo")
       strings("bar")

Build and run.

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Class Foo with a=1 and b="hi".
   Class Foo with a=2 and b="ho".
   Class Foo.
   Class Bar.
   Other class: Fie()
   Zero integer.
   Five integer.
   String foo.
   Other string: bar

.. _pattern_matching example: https://github.com/mys-lang/mys/tree/main/examples/pattern_matching
