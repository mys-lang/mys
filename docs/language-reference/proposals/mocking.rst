Mocking
-------

``mock()`` is a builtin function to create mock objects. Mock
functions with ``mock(function)`` and methods with ``mock(class,
method)``. Returned mock objects have these methods:

.. code-block:: mys

   # Expect given parameters.
   func expect(self, <parameters>) -> MockCall

   # Call given object's call method instead instead of the real
   # function or method.
   func replace(self, object) -> MockCall

   # Return given value.
   func returns(self, result) -> MockCall

   # Raise given exception.
   func raises(self, exception) -> MockCall

   # Expect the mock to be called count times.
   func repeat(self, count: i64 = -1)

Mock calls have these methods:

.. code-block:: mys

   # Return given value.
   func returns(self, result) -> MockCall

   # Raise given exception.
   func raises(self, exception) -> MockCall

   # Expect the mock call to be called count times.
   func repeat(self, count: i64 = -1)

Examples
^^^^^^^^

The third party ``fie`` module that we want to mock in the examples
below.

.. code-block:: mys

   class Foo:

       func bar(self) -> bool:
           return False

   func fum(value: i64) -> i64:
       return -1

Mocking a function
^^^^^^^^^^^^^^^^^^

An example that mocks the ``fum()`` function.

.. code-block:: mys

   from fie import fum

   func foo(value: i64) -> i64:
       return 2 * fum(value)

   @test
   func test_foo():
       mock(fum).expect(1).returns(2)
       mock(fum).expect(4).returns(5)

       assert foo(1) == 4
       assert foo(4) == 10

       # Fails since only two calls to fum() were expected.
       foo(10)

Mocking a method
^^^^^^^^^^^^^^^^

An example that mocks the ``bar()`` method.

.. code-block:: mys

   from fie import Foo

   func foo() -> bool:
       return Foo().bar()

   @test
   func test_foo_many_calls():
       mock(Foo, bar).returns(True).repeat()
       assert foo()
       assert foo()
       assert foo()

   class _MyBar(mock(Foo, bar)):

       func call(self, object: Foo) -> bool:
           return True

   @test
   func test_foo_replace():
       # Call _MyBar's call() method instead of the real bar method.
       mock(Foo, bar).replace(_MyBar())
       assert foo()
