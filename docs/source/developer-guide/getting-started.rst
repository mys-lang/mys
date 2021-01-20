Getting started
---------------

Development environment
^^^^^^^^^^^^^^^^^^^^^^^

Ubuntu
""""""

Install tools, clone the repo and run tests and examples.

.. code-block:: text

   $ sudo apt install git g++ make pylint ccache
   $ git clone ssh://git@github.com/mys-lang/mys
   $ python -m pip install -r mys/requirements.txt
   $ python -m pip install coverage pylint
   $ cd mys
   $ make

Windows
"""""""

The Mys project is built in Cygwin.

#. Install `Cygwin`_. Required packages are ``gcc-g++``, ``make``,
   ``python38``, ``ccache``, ``git``, ``libtool``, ``automake`` and
   ``python38-devel``.

#. Start Cygwin and do the following one time setup.

   .. code-block:: text

      $ ln -s /usr/bin/python3.8 /usr/bin/python
      $ python -m easy_install pip
      $ git clone ssh://git@github.com/mys-lang/mys
      $ python -m pip install -r mys/requirements.txt
      $ python -m pip install coverage pylint

#. Run tests and examples.

   .. code-block:: text

      $ cd mys
      $ make

Tips and tricks
^^^^^^^^^^^^^^^

It's usually a good idea to add a test in ``tests/files/<name>.mys``
and execute with ``make test -j 8 ARGS="-k <pattern>``.

Add positive and negative tests.

Build and run all tests in parallel with ``make test-parallel -j 8``.

Build and run all tests in parallel and all examples with ``make -j 8``.

Open ``htmlcov/index.html`` for code coverage.

``make help`` shows a list of all available make targets.

.. _Cygwin: https://www.cygwin.com/
