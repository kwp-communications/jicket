Mail Template
====================

The contents of the confirmation mail is generated from a template. Some variables can be accessed to dynamically
generate a response to incoming emails.


Template syntax
------------------------
The template should be written as valid HTML, just as if you would write a regular mail. You can place named substitutes
for use with string interpolation in your template. The syntax for them is ``%(NAME)TYPE``. For example, if you want the
subject as a string, you'd put ``$(subject)s`` at the appropriate location in your template. See
:ref:`interpolation-vars` for a list of available variables.

An example template could look like this:

.. code-block:: html

    <html>
      <head></head>
      <body>
        <p>Hello!<br>
            <br>
            Thank you for contacting the support. This mail indicates that your ticket has been successfully created and will be processed soon.<br>
            Please always keep the Ticket-ID in the subject, otherwise we won't be able to track your issue properly.<br>
            <br>
            <br>
            Ticket ID: %(ticketid)s<br>
            Ticket Subject: %(subject)s<br>
            <br>
            <br>
            This mail was automatically generated by <a href="https://github.com/kwp-communications/jicket">Jicket</a>
        </p>
      </body>
    </html>


.. _interpolation-vars:

Interpolation variables
----------------------------

Subject
""""""""""""""""""""""""""""""""""
:Name:          ``subject``
:Type:          ``s``
:Description:   Subject of ticket
:Example:       Re: The Website Is Down


Ticket ID
""""""""""""""""""""""""""""""""""
:Name:          ``ticketid``
:Type:          ``s``
:Description:   Hashed ID of ticket
:Example:       K6NPD4