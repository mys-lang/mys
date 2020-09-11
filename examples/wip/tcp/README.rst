TCP networking
==============

Start a TCP server in one terminal. It waits for clients to connect
and echos any received data.

.. code-block:: text

   $ mys run server
   Accepting clients on 127.0.0.1:3232.
   Client accepted.
   Received 'Hello!'.
   Sending 'Hello!'.
   Closed.

Start a TCP client in another terminal. It connects to the server and
writes ``Hello!`` to it. The server responds with the same data and
then the connections is closed.

.. code-block:: text

   $ mys run client
   Connecting to 127.0.0.1:3232.
   Connected.
   Sending 'Hello!'.
   Received 'Hello!'.
   Closing.
