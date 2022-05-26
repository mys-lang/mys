Statistics
==========

Website statistics.

Start date and time
-------------------

{website-start-date-time}

Traffic
-------

Unique visitors
^^^^^^^^^^^^^^^

Number of unique visitors: {website-number-of-unique-visitors}

.. image:: _static/world.svg

- Green: Latest request succeeded.

- Red: Latest request failed.

Requests
^^^^^^^^

Number of requests: {website-number-of-requests}

{website-requests}

Referring sites
^^^^^^^^^^^^^^^

{website-referrers}

API
---

There is a `GraphQL`_ end-point, https://mys-lang.org/graphql, that
provides statistics.

Use for example https://graphiql-online.com or
https://studio.apollographql.com/sandbox to explore the API.

One can also use ``curl`` and ``jq`` if the query is known:

.. code-block:: text

   ❯ curl -s -X POST https://mys-lang.org/graphql \
          -d '{"query":"{statistics{total_number_of_requests}}"}' | jq
   {
     "data": {
       "statistics": {
         "total_number_of_requests": 89
       }
     }
   }

.. _GraphQL: https://graphql.org
