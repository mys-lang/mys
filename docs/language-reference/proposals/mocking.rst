Mocking
-------

``mock()`` is a builtin function to create mock objects. Mock
functions with ``mock(function)`` and methods with ``mock(class,
method)``. Returned mock objects have methods as below.

.. code-block:: mys

   # Assert given parameters and then return given value or raise given
   # exception. Do this count times. Give count as -1 to allow any number
   # of calls.
   def call(self, <parameters>, <result>, raises=None, count=1)

   # Call given function instead instead of the real function or method.
   # Do this count times. Give count as -1 to allow any number of calls.
   def call(self, function, count=1)

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
   def test_foo_per_call():
       mock(fum).call(1, 2)
       mock(fum).call(4, 5)

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

   def my_bar(obj: Foo) -> bool:
       return False

   @test
   def test_foo_every_call():
       # All calls to Foo's bar method returns True.
       mock(Foo, bar).call(True, count=-1)
       assert foo()
       assert foo()
       assert foo()

       # Call my_bar instead of the real bar method.
       mock(Foo, bar).call(my_bar)
       assert not foo()
