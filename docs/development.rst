Development
===========

To simplify the development workflow, the project provides a docker container that can run the tests.

You will need `docker <https://www.docker.com/>`_ and `Docker Compose <https://docs.docker.com/compose/>`_.

.. code-block:: bash

    docker-compose run --rm django test
