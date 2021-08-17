Mocking
-------

Based on https://github.com/eerimoq/nala.

Mock API
^^^^^^^^

``mock()`` is a builtin function to create mock objects. Mock
functions with ``mock(function)`` and methods with ``mock(class,
method)``. Returned mock objects have methods as below.

Same behaviour for every call
"""""""""""""""""""""""""""""

.. code-block:: mys

   def call(self, <params>, <res>, raises=None) # Check parameters and return.
   def call_none(self)                          # No calls allowed.
   def call_implementation(self, function)      # Replace implementation.
   def call_real(self)                          # Real implementation.

An example mocking a function:

.. code-block:: mys

   def foo(value: i64) -> i64:
       return -1

   @test
   def test_foo_every_call):
       mock(foo).call(1, 2)

       # All calls to foo() expects its parameter to be 1 and returns 2.
       assert foo(1) == 2
       assert foo(1) == 2

An example mocking a method:

.. code-block:: mys

   class Foo:

       def bar(self) -> bool:
           return False

   @test
   def test_foo_every_call):
       foo = Foo()

       # All calls to Foo's bar method returns True.
       mock(Foo, bar).call(True)
       assert foo.bar()

       # Call real implementation again.
       Foo_bar_mock_real()
       assert not foo.bar()

Per call control
""""""""""""""""

.. code-block:: mys

   def call_once(self, <params>, <res>, raises=None) # Check parameters and return
                                                     # once (per call).
   def call_real_once(self)                          # Real implementation once (per call).

An example:

.. code-block:: mys

   def foo(value: i64) -> i64:
       return -1

   @test
   def test_foo_per_call():
       mock(foo).call_once(1, 2)
       mock(foo).call_once(4, 5)

       # First call to foo() expects its parameter to be 1 and returns 2.
       assert foo(1) == 2

       # Second call to foo() expects its parameter to be 4 and returns 5.
       assert foo(4) == 5

       # Third call will fail and the test will end.
       foo(10)
