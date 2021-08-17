Mocking
-------

Based on https://github.com/eerimoq/nala.

Mock API
^^^^^^^^

A function mock will call the real implementation by default. Use the
functions below to control mock object behaviour.

For all functions and methods
"""""""""""""""""""""""""""""

Same behaviour for every call.

.. code-block:: mys

   FUNC_mock(<params>, <res>)     # Check parameters and return.
   FUNC_mock_ignore_in(<res>)     # Ignore parameters and return.
   FUNC_mock_none()               # No calls allowed.
   FUNC_mock_implementation(*)    # Replace implementation.
   FUNC_mock_real()               # Real implementation.

   # Same as above, but for methods.
   CLASS_METHOD_mock(<params>, <res>)
   CLASS_METHOD_mock_ignore_in(<res>)
   CLASS_METHOD_mock_none()
   CLASS_METHOD_mock_implementation(*)
   CLASS_METHOD_mock_real()

An example mocking a function:

.. code-block:: mys

   def foo(value: i64) -> i64:
       return -1

   @test
   def test_foo_every_call):
       foo_mock(1, 2)

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
       Foo_bar_mock(True)
       assert foo.bar()

       # Call real implementation again.
       Foo_bar_mock_real()
       assert not foo.bar()

Per call control.

.. code-block:: mys

   FUNC_mock_once(<params>, <res>) -> i64 # Check parameters and return once (per call).
                                          # Returns a mock instance handle.
   FUNC_mock_ignore_in_once(<res>) -> i64 # Ignore parameters and return once
                                          # (per call). Returns a mock instance handle.
   FUNC_mock_real_once()                  # Real implementation once (per call).

   CLASS_METHOD_mock_once(<params>, <res>) -> i64
   CLASS_METHOD_mock_ignore_in_once(<res>) -> i64
   CLASS_METHOD_mock_real_once()

An example:

.. code-block:: mys

   # def foo(value: i64) -> i64

   @test
   def test_foo_per_call():
       foo_mock_once(1, 2)
       foo_mock_once(4, 5)

       # First call to foo() expects its parameter to be 1 and returns 2.
       assert foo(1) == 2

       # Second call to foo() expects its parameter to be 4 and returns 5.
       assert foo(4) == 5

       # Third call will fail and the test will end.
       foo(10)

For function parameters part of <params>
""""""""""""""""""""""""""""""""""""""""

Changes the behaviour of currect mock object (most recent ``*_mock()``
or ``*_mock_once()`` call). Works for both per call and every call
functions above.

.. code-block:: mys

   FUNC_mock_ignore_PARAM_in()        # Ignore on input.

   CLASS_METHOD_mock_ignore_PARAM_in()

An example:

.. code-block:: mys

   # def foo(value: i64)

   @test
   def test_foo_ignore_value():
       foo_mock_once(1, 2)
       foo_mock_ignore_value_in()

       assert foo(9) == 2
