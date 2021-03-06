Classes and traits
------------------

- Instance members are accessed with ``<object>.<variable/method>``.

- Automatically added methods (``__init__()``, ``__str__()``, ...)
  are only added if missing.

- Decorate a class with ``@trait`` to make it a trait.

  ToDo: Introduce the trait keyword?

- Traits cannot have members.

- Traits cannot be instantiated, only classes can.

- Implemented trait methods must be decorated with ``@trait(T)`` or
  ``@trait(T, <method>)``.

- A class can implement zero or more traits.

- Destructors may not raise exceptions.

Example 1
^^^^^^^^^

A class with a member ``value`` and a method ``inc()``.

The constructor ``def __init__(self, value: i32)`` (and more methods)
are automatically added to the class as they are missing.

.. code-block:: python

   class Foo:
       value: i32

       def inc(self):
           self.value += 1

   def main():
       print("f1:")
       f1 = Foo(0)
       print(f1)
       f1.inc()
       print(f1)

       print("f2:")
       f2 = Foo(5)
       print(f2)

.. code-block:: text

   $ mys run
   f1:
   Foo(value=0)
   Foo(value=1)
   f2:
   Foo(value=5)

Example 2
^^^^^^^^^

An example of how to use traits.

.. code-block:: python

   @trait
   class Base:

       def add(self, value: i64) -> i64:
           pass

       def surprise(self, value: i64) -> i64:
           # Default implementation.
           return value * value

   class Foo(Base):

       @trait(Base)
       def add(self, value: i64) -> i64:
           return value + 5

       def mul(self, value: i64) -> i64:
           return value * 3

   class Bar(Base):

       @trait(Base)
       def add(self, value: i64) -> i64:
           return value + 10

       @trait(Base)
       def surprise(self, value: i64) -> i64:
           return value * value * value

       def div(self, value: i64) -> i64:
           return value / 3

   def calc(base: Base, value: i64):
       print(f"base.add({value}):", base.add(value))
       print(f"base.surprise({value}):", base.surprise(value))

       match base:
           case Foo() as foo:
               print(f"foo.mul({value}):", foo.mul(value))
           case Bar() as bar:
               print(f"bar.div({value}):", bar.div(value))

   def main():
       value = 12
       calc(Foo(), value)
       calc(Bar(), value)

.. code-block:: text

   $ mys run
   base.add(12): 17
   base.surprise(12): 144
   foo.mul(12): 36
   base.add(12): 22
   base.surprise(12): 1728
   bar.div(12): 4

Example 3
^^^^^^^^^

A class that implements two traits where both traits has the method
``work()``. One of the two must be renamed in the implementing class.

.. code-block:: python

   @trait
   class Base1:

       def work(self):
           pass

   @trait
   class Base2:

       def work(self):
           pass

   class Foo(Base1, Base2):

       @trait(Base1)
       def work(self):
           print("work()")

       # Must rename due to name clash.
       @trait(Base2, work)
       def work_2(self):
           print("work_2()")

   def base_1_work(base: Base1):
       base.work()

   def base_2_work(base: Base2):
       # Calls Foo's work_2() method.
       base.work()

   def main():
       foo = Foo()
       foo.work()
       foo.work_2()
       base_1_work(foo)
       base_2_work(foo)

.. code-block:: text

   $ mys run
   work()
   work_2()
   work()
   work_2()

Example 4
^^^^^^^^^

Make the implemented trait method private by renaming it in the
implementing class.

.. code-block:: python

   @trait
   class Base:

       def work(self):
           pass

   class Foo(Base):

       @trait(Base, work)
       def _work(self):
           print("_work()")

   def work(base: Base):
       base.work()

   def main():
       foo = Foo()
       # Cannot call foo.work() as that method does not exist on the class.
       work(foo)

.. code-block:: text

   $ mys run
   _work()

Example 5
^^^^^^^^^

The class has a method that name clashes with a trait method. Rename
implemented trait method in the class.

.. code-block:: python

   @trait
   class Base:

       def work(self):
           pass

   class Foo(Base):

       def work(self):
           print("work()")

       @trait(Base, work)
       def work_2(self):
           print("work_2()")

   def work(base: Base):
       base.work()

   def main():
       foo = Foo()
       foo.work()
       foo.work_2()
       work(foo)

.. code-block:: text

   $ mys run
   work()
   work_2()
   work_2()

Example 6
^^^^^^^^^

Trait methods can call methods in the same trait, any functions and
classes and use global variables.

.. code-block:: python

   def age() -> i64:
       return 5

   @trait
   class Formatter:

       def format(self) -> string:
           # Calling method name() and function age().
           return f"Name: {self.name()}, Age: {age()}"

       def name(self) -> string:
           pass

   class Foo(Formatter):

       def name(self) -> string:
           return "Bob"

   def main():
       foo = Foo()
       print(foo.format())

.. code-block:: text

   $ mys run
   Name: Bob, Age: 5

Ideas
^^^^^

Ideas on how to implement traits and classes to remove Object base
class limitation. It is problematic when a class implements multiple
traits, at least when all traits inherits from it.

.. code-block:: c++

   class Base1 {
   public:
       virtual i64 Base1_work() = 0;
       virtual String Base1___str__() = 0;
   };

   class Base2 {
   public:
       virtual i64 Base2_work() = 0;
       virtual String Base2___str__() = 0;
   };

   class Foo : public Base1, public Base2 {
   public:
       i64 Base1_work()
       {
           return 1;
       }

       i64 Base2_work()
       {
           return 2;
       }

       String Base1___str__()
       {
           return __str__();
       }

       String Base2___str__()
       {
           return __str__();
       }

       String __str__()
       {
           return "Foo()";
       }
   };
