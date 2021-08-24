Mocking
-------

``mock()`` is a builtin function to create mock objects. Mock
functions with ``mock(function)`` and methods with ``mock(class,
method)``. Returned mock objects have these methods:

.. code-block:: mys

   # Expect given parameters.
   def expect(self, <parameters>) -> MockCall

   # Call given object's call method instead instead of the real
   # function or method.
   def replace(self, object) -> MockCall

   # Return given value.
   def returns(self, result) -> MockCall

   # Raise given exception.
   def raises(self, exception) -> MockCall

   # Expect the mock to be called count times.
   def count(self, value: i64)

Mock calls have these methods:

.. code-block:: mys

   # Return given value.
   def returns(self, result) -> MockCall

   # Raise given exception.
   def raises(self, exception) -> MockCall

   # Expect the mock call to be called count times.
   def count(self, value: i64)

Examples
^^^^^^^^

The third party ``fie`` module that we want to mock in the examples
below.

.. code-block:: mys

   class Foo:

       def bar(self) -> bool:
           return False

   def fum(value: i64) -> i64:
       return -1

Mocking a function
^^^^^^^^^^^^^^^^^^

An example that mocks the ``fum()`` function.

.. code-block:: mys

   from fie import fum

   def foo(value: i64) -> i64:
       return 2 * fum(value)

   @test
   def test_foo():
       mock(fum).expect(1).returns(2)
       mock(fum).expect(4).returns(5)

       # First call to fum() expects its parameter to be 1 and returns 2, hence
       # foo() returns 4 (2 * 2).
       assert foo(1) == 4

       # Second call to fum() expects its parameter to be 4 and returns 5, hence
       # foo() returns 10 (2 * 5).
       assert foo(4) == 10

       # Third call will fail and the test will end since only two calls were
       # expected.
       foo(10)

Mocking a method
^^^^^^^^^^^^^^^^

An example that mocks the ``bar()`` method.

.. code-block:: mys

   from fie import Foo

   def foo() -> bool:
       return Foo().bar()

   @test
   def test_foo_many_calls():
       # All calls to Foo's bar method returns True.
       mock(Foo, bar).returns(True).count(-1)
       assert foo()
       assert foo()
       assert foo()

   class MyBar(Mock_Foo_bar):

       def call(self, object: Foo) -> bool:
           return False

   @test
   def test_foo_replace():
       # Call MyBar's call() method instead of the real bar method.
       mock(Foo, bar).replace(MyBar())
       assert not foo()
