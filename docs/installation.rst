Installation
==================================

Jicket can be installed like any other python package. Additionally a convenient docker image is provided.

Jicket requires at least Python 3.6 to run.


Docker
----------------------------------
Running jicket in a docker container is a convenient way to get started quickly or for testing it locally without having
to worry about setting up the environment. You need to pass it some minimum configuration (mostly IMAP, SMTP and Jira
account data) to get it running.

`Jicket on Docker Hub <https://hub.docker.com/r/kwpcommunications/jicket/>`_

Running
^^^^^^^^^
Create a file ``env.list`` to store your environment variables. Make sure the rights for accessing the file are set
correctly, especially the global read flag (``chmod o-rwx env.list``). Configure the environment variables according to
:doc:`configuration` in a ``VAR=value`` format, e.g.:

.. code-block:: text
  :caption: env.list

  JICKET_IMAP_HOST=imap.example.com
  JICKET_IMAP_PORT=993
  JICKET_IMAP_USER=foo@example.com
  JICKET_IMAP_PASS=correcthorsebatterystaple

The container is then launched:

  >>> docker run -it --env-file env.list jicket



pip
----------------------------------

Install the jicket package with pip:

  >>> pip install jicket

Afterwards jicket can be launched with

  >>> jicket