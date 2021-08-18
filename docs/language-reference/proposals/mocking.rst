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

   from fie import bar

   def foo(value: i64) -> i64:
       return 2 * bar(value)

   @test
   def test_foo_every_call():
       # All calls to bar() expects its parameter to be 1 and returns 2, hence
       # foo() returns 4 (2 * 2).
       mock(bar).call(1, 2)
       assert foo(1) == 4
       assert foo(1) == 4

An example mocking a method:

.. code-block:: mys

   from fie import Foo

   @test
   def test_foo_every_call():
       foo = Foo()

       # All calls to Foo's bar method returns True.
       mock(Foo, bar).call(True)
       assert foo.bar()

       # Call real implementation again.
       mock(Foo, bar).call_real()
       assert not foo.bar()

The fie module:

.. code-block:: mys

   class Foo:

       def bar(self) -> bool:
           return False

   def bar(value: i64) -> i64:
       return -1

Per call control
""""""""""""""""

.. code-block:: mys

   def call_once(self, <params>, <res>, raises=None) # Check parameters and return
                                                     # once (per call).
   def call_real_once(self)                          # Real implementation once (per call).

An example:

.. code-block:: mys

   from fie import bar

   def foo(value: i64) -> i64:
       return 2 * bar(value)

   @test
   def test_foo_per_call():
       mock(bar).call_once(1, 2)
       mock(bar).call_once(4, 5)

       # First call to bar() expects its parameter to be 1 and returns 2, hence
       # foo() returns 4 (2 * 2).
       assert foo(1) == 4

       # Second call to bar() expects its parameter to be 4 and returns 5, hence
       # foo() returns 10 (2 * 5).
       assert foo(4) == 10

       # Third call will fail and the test will end since only two calls were
       # expected.
       foo(10)
