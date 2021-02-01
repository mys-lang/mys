Installation
============

Linux
^^^^^

#. Install recent versions of ``g++``, ``make``, ``pylint``,
   ``ccache``, ``libtool``, ``automake`` and ``wget``.

#. Install Python 3.8 or later, and then install Mys using ``pip``.

   .. code-block:: bash

      $ sudo pip install mys

#. Run ``mys`` to make sure it was installed successfully.

   .. code-block:: bash

      $ mys

Windows
^^^^^^^

#. Install `Cygwin`_. Required packages are ``gcc-g++``, ``make``,
   ``python38``, ``python38-devel``, ``ccache``, ``libtool``,
   ``automake`` and ``wget``.

#. Start Cygwin and install ``pip`` and Mys.

   .. code-block:: text

      $ ln -s /usr/bin/python3.8 /usr/bin/python
      $ python -m easy_install pip
      $ python -m pip install mys

#. Run ``mys`` to make sure it was installed successfully.

   .. code-block:: bash

      $ mys

.. _Cygwin: https://www.cygwin.com/
