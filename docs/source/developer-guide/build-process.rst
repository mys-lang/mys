Build process
-------------

``mys build``, ``mys run`` and ``mys test`` does the following:

#. Use Python's parser to transform the source code to an Abstract
   Syntax Tree (AST).

#. Generate C++ code from the AST.

#. Compile the C++ code with ``g++``.

#. Link the application with ``g++``.
