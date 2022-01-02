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

Special methods
^^^^^^^^^^^^^^^

+---------------------------------+-------------+---------------------------------------------+
| Name                            | Usage       | Comment                                     |
+=================================+=============+=============================================+
| ``__init__(self)``              | ``Foo()``   | Constructor.                                |
+---------------------------------+-------------+---------------------------------------------+
| ``__str__(self) -> string``     | ``str(o)``  | String representation, often for debugging. |
+---------------------------------+-------------+---------------------------------------------+
| ``__len__(self) -> u64``        | ``len(o)``  | Length.                                     |
+---------------------------------+-------------+---------------------------------------------+
| ``__eq__(self, other) -> bool`` | ``a == b``  | Equal to other object.                      |
+---------------------------------+-------------+---------------------------------------------+
| ``__lt__(self, other) -> bool`` | ``a < b``   | Less than other object.                     |
+---------------------------------+-------------+---------------------------------------------+
| ``__hash__(self) -> i64``       | ``hash(o)`` | Hash.                                       |
+---------------------------------+-------------+---------------------------------------------+

Example 1
^^^^^^^^^

A class with a member ``value`` and a method ``inc()``.

The constructor ``def __init__(self, value: i32)`` (and more methods)
are automatically added to the class as they are missing.

.. code-block:: mys

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

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   f1:
   Foo(value=0)
   Foo(value=1)
   f2:
   Foo(value=5)

Example 2
^^^^^^^^^

An example of how to use traits.

.. code-block:: mys

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

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
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

.. code-block:: mys

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

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   work()
   work_2()
   work()
   work_2()

Example 4
^^^^^^^^^

Make the implemented trait method private by renaming it in the
implementing class.

.. code-block:: mys

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

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   _work()

Example 5
^^^^^^^^^

The class has a method that name clashes with a trait method. Rename
implemented trait method in the class.

.. code-block:: mys

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

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   work()
   work_2()
   work_2()

Example 6
^^^^^^^^^

Trait methods can call methods in the same trait, any functions and
classes and use global variables.

.. code-block:: mys

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

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   Name: Bob, Age: 5

Ideas
^^^^^

Ideas on how to implement traits and classes to remove Object base
class limitation. It is problematic when a class implements multiple
traits, at least when all traits inherits from it.

Example 3
"""""""""

.. code-block:: c++

   class Base1 {
   public:
       virtual void Base1_work() = 0;
       virtual String Base1___str__() = 0;
   };

   class Base2 {
   public:
       virtual void Base2_work() = 0;
       virtual String Base2___str__() = 0;
   };

   class Foo : public Base1, public Base2 {
   public:
       void Base1_work() override;
       void Base2_work() override;
       String Base1___str__() override;
       String Base2___str__() override;
       String __str__();
   };

   void Foo::Base1_work()
   {
       std::cout << "work()" << "\n";
   }

   void Foo::Base2_work()
   {
       std::cout << "work_2()" << "\n";
   }

   String Foo::Base1___str__()
   {
       return __str__();
   }

   String Foo::Base2___str__()
   {
       return __str__();
   }

   String Foo::__str__()
   {
       return "Foo()";
   }

Example 6
"""""""""

.. code-block:: c++

   i64 age()
   {
       return 5;
   }

   class Formatter {
   public:
       virtual String Formatter_format();
       virtual String Formatter_name() = 0;
       virtual String Formatter___str__() = 0;
   };

   String Formatter::Formatter_format()
   {
       return String("Name: ") + name() + String(", Age: ") + age();
   }

   class Foo : public Formatter {
   public:
       String Formatter_name() override;
       String Formatter___str__();
       String __str__();
   };

   String Foo::Formatter_name()
   {
       return String("Bob");
   }

   String Foo::Formatter___str__() override
   {
       return __str__();
   }

   String Foo::__str__()
   {
       return "Foo()";
   }
