Copy
----

- Copy objects with the builtin functions ``copy()`` and
  ``deepcopy()``.

- The ``__copy__(self, other: Self)`` method implements ``copy()`` and
  the ``__deepcopy__(self, other: Self)`` method implements
  ``deepcopy()``. Both have default implementations that simply copies
  all members.

Example
^^^^^^^

.. code-block:: mys

   class Foo:
       a: i64
       b: string

   class Bar:
       foo: Foo

   func main():
       foo = Foo(5, "bar")
       foo_copy = copy(foo)
       assert foo == foo_copy
       assert foo is not foo_copy

       bar = Bar(foo)
       bar_copy = copy(bar)
       assert bar_copy.foo is bar.foo
       bar_deepcopy = deepcopy(bar)
       assert bar_deepcopy.foo is not bar.foo

.. code-block:: mys

   class Foo:

       func __copy__(self, other: Foo):
           raise NotImplementedError()

       func __deepcopy__(self, other: Foo):
           raise NotImplementedError()

   func main():
       try:
           print(copy(Foo()))
       except NotImplementedError:
           pass

       try:
           print(deepcopy(Foo()))
       except NotImplementedError:
           pass
