Installation
============

Linux
^^^^^

Install Python 3.8 or later, and then install Mys using ``pip``.

.. code-block:: bash

   $ pip install mys

You must also have recent versions of ``g++``, ``make`` and ``pylint``
installed. It's highly recommended to install ``ccache`` as well for
faster builds.

Windows
^^^^^^^

#. Install `Cygwin`_. Required packages are ``gcc-g++``, ``make``,
   ``python38`` and ``python38-devel``. It's highly recommended to
   select ``ccache`` as well for faster builds.

#. Start Cygwin and install ``pip`` and Mys.

   .. code-block:: text

      $ /usr/bin/python3.8 -m easy_install pip
      $ /usr/bin/python3.8 -m pip mys

.. _Cygwin: https://www.cygwin.com/
