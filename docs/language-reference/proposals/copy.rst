Copy
----

- Copy objects with ``copy()`` and ``deepcopy()``.

- ``__copy__(self, other: Self)`` implements ``copy()`` and
  ``__deepcopy__(self, other: Self, memo: {string: string})``
  implements ``deepcopy()``. Both have default implementations.

Example
^^^^^^^

.. code-block:: mys

   class Foo:
       a: i64
       b: string

   class Bar:
       foo: Foo

   def main():
       foo = Foo(5, "bar")
       foo_copy = copy(foo)
       assert foo == foo_copy
       assert foo is not foo_copy

       bar = Bar(foo)
       bar_copy = copy(bar)
       assert bar_copy.foo is bar.foo
       bar_deepcopy = deepcopy(bar)
       assert bar_deepcopy.foo is not bar.foo
