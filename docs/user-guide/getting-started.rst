Getting started
---------------

#. Install Mys as described on the :doc:`installation` page.

#. Create a package called ``foo`` with the command ``mys new foo``,
   and then enter it. This package is used in throughout the tutorial.

   .. image:: ../_static/new.png

   ``src/main.mys`` implements the hello world application.

   .. code-block:: python

      def main():
          print("Hello, world!")

#. Build and run the application with the command ``mys run``. It
   prints ``Hello, world!``, just as expected.

   .. image:: ../_static/run.png

#. ``src/lib.mys`` implements the function ``add()`` and its test
   ``test_add()``. This examplifies how to test your Mys modules.

   .. code-block:: python

      def add(first: i32, second: i32) -> i32:
          return first + second

      @test
      def test_add():
          assert add(1, 2) == 3

#. Build and run the tests with the command ``mys test``.

   .. image:: ../_static/test.png

#. Add the `bar package`_ as a dependency and use its ``hello()``
   function.

   ``package.toml`` with the ``bar`` dependency added:

   .. code-block:: toml

      [package]
      name = "foo"
      version = "0.1.0"
      authors = ["Mys Lang <mys.lang@example.com>"]
      description = "Add a short package description here."

      [dependencies]
      bar = "latest"

   ``src/main.mys`` importing ``hello()`` from the ``bar`` module:

   .. code-block:: python

      from bar import hello

      def main(argv: [string]):
          hello(argv[1])

#. Build and run the new application. Notice how the dependency is
   downloaded and that ``mys run universe`` prints ``Hello,
   universe!``.

   .. image:: ../_static/run-universe.png

#. Replace the code in ``src/main.mys`` with the code below. It
   examplifies how to use functions, :doc:`classes
   <../language-reference/classes-and-traits>`, :doc:`errors
   <../language-reference/errors>`, :doc:`types
   <../language-reference/types>` and command line arguments. The
   syntax is almost identical to Python, so many readers should easily
   understand it.

   .. code-block:: python

      def func_1(a: i64) -> (i64, string):
          if a == 5:
              text = "Foo"
          else:
              text = "Bar"

          return 2 * a, text

      def func_2(a: i64, b: i64) -> i64:
          for i in range(b):
              a += i * b

          return a

      def func_3(a: i64) -> {i64: [f64]}:
          return {
              1: [2.0],
              10 * a: [7.5, -1.0]
          }

      def func_4():
          try:
              raise ValueError()
          except:
              print("func_4():      An error occurred.")

      def func_5() -> [i64]:
          small: [i64] = []

          for v in [3, 1, 5, 7, 2]:
              if v < 5:
                  small.append(v)

          small.sort()
          small.reverse()

          return small

      class Calc:
          value: i64

          def triple(self):
              self.value *= 3

      def main(argv: [string]):
          value = i64(argv[1])
          print("func_1(value):", func_1(value))
          print("func_2(value):", func_2(value, 1))
          print("func_3(value):", func_3(value))
          func_4()
          print("func_5():     ", func_5())
          calc = Calc(value)
          calc.triple()
          print("calc:         ", calc)

#. Build and run it with ``mys run 5``.

   .. image:: ../_static/run-features.png

#. Continue to explore Mys by reading the :doc:`../language-reference`,
   and at the same time modify the code in ``src/main.mys`` to test
   anything you find interesting.

.. _bar package: https://github.com/mys-lang/bar
