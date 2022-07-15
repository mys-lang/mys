Special symbols
---------------

Special symbols with different properties.

+-------------------+------------+------------------------------------------+
| Name              | Type       | Description                              |
+===================+============+==========================================+
| ``__assets__``    | ``string`` | The module's assets path.                |
+-------------------+------------+------------------------------------------+
| ``__file__``      | ``string`` | The module file path.                    |
+-------------------+------------+------------------------------------------+
|  ``__line__``     | ``i64``    | The line in the module file.             |
+-------------------+------------+------------------------------------------+
|  ``__name__``     | ``string`` | The module name (including package).     |
+-------------------+------------+------------------------------------------+
| ``__unique_id__`` | ``i64``    | A unique integer. May change on rebuild. |
+-------------------+------------+------------------------------------------+
| ``__version__``   | ``string`` | The module's package version.            |
+-------------------+------------+------------------------------------------+

Sample usage:

.. code-block:: mys

   func main():
       print("__assets__:   ", __assets__)
       print("__file__:     ", __file__)
       print("__line__:     ", __line__)
       print("__name__:     ", __name__)
       print("__unique_id__:", __unique_id__)
       print("__unique_id__:", __unique_id__)
       print("__unique_id__:", __unique_id__)
       print("__line__:     ", __line__)
       print("__version__:  ", __version__)

Build and run:

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.21 seconds)
   __assets__:    /Users/erik/workspace/mys/foo/build/speed/app-assets/foo
   __file__:      ./src/main.mys
   __line__:      4
   __name__:      foo.main
   __unique_id__: 1
   __unique_id__: 2
   __unique_id__: 3
   __line__:      9
   __version__:   0.1.0
