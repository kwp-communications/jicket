Configuration
==================================

Jicket can be configured using both environment variables and command line arguments.
Command line arguments take precedence over environment variables.

.. warning:: Using environment variables for configuring the username and password is highly recommended.
             If you pass them as command line arguments, they show up in the process list and will be readable for
             anyone with even basic access to the server.


IMAP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Configuration of the IMAP mailbox that is used to read incoming mails from.

Host
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_IMAP_HOST``
:CLI:           ``--imaphost``
:Type:          ``str``
:Required:      Yes
:Description:   URL of IMAP mailbox that is receiving new ticket emails
:Example:       ``imap.example.com``

Port
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_IMAP_PORT``
:CLI:           ``--imaphost``
:Type:          ``int``
:Default:       ``993``
:Required:      No
:Description:   Port of IMAP host
:Example:       ``993``

User
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_IMAP_USER``
:CLI:           ``--imapuser``
:Type:          ``str``
:Required:      Yes
:Description:   Username for IMAP mailbox
:Example:       ``foo@example.com``

Password
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_IMAP_PASS``
:CLI:           ``--imappass``
:Type:          ``str``
:Required:      Yes
:Description:   Password for IMAP user
:Example:       ``correcthorsebatterystaple``



SMTP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Configuration of the SMTP server that is used to send emails from.

Host
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_SMTP_HOST``
:CLI:           ``--smtphost``
:Type:          ``str``
:Required:      Yes
:Description:   URL of SMTP server used to send out emails
:Example:       ``smtp.example.com``

Port
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_SMTP_PORT``
:CLI:           ``--smtphost``
:Type:          ``int``
:Default:       ``587``
:Required:      No
:Description:   Port of SMTP server
:Example:       ``587``

User
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_smtp_USER``
:CLI:           ``--smtpuser``
:Type:          ``str``
:Required:      No
:Description:   Username for SMTP server. If it is not explicitly provided, IMAP username will be used.
:Example:       ``foo@example.com``

Password
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_SMTP_PASS``
:CLI:           ``--smtppass``
:Type:          ``str``
:Required:      No
:Description:   Password for SMTP user.  If it is not explicitly provided, IMAP password will be used.
:Example:       ``correcthorsebatterystaple``



Jira
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Configuration of jira instance on which new issues shall be created from incoming emails.

URL
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_JIRA_URL``
:CLI:           ``--jiraurl``
:Type:          ``str``
:Required:      Yes
:Description:   URL of Jira instance that shall be used
:Example:       ``jira.example.com``

User
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_JIRA_USER``
:CLI:           ``--jirauser``
:Type:          ``str``
:Required:      Yes
:Description:   Username for Jira access
:Example:       ``foo@example.com``

Password
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_JIRA_PASS``
:CLI:           ``--jirapass``
:Type:          ``str``
:Required:      Yes
:Description:   Password for Jira user
:Example:       ``correcthorsebatterystaple``

Project
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_JIRA_PROJECT``
:CLI:           ``--jiraproject``
:Type:          ``str``
:Required:      Yes
:Description:   The Project key in which new issues shall be created. It can be found in the URL of your project.
:Example:       ``SHD``

Email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Configuration regarding the mailbox and emails in general

Inbox
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_FOLDER_INBOX``
:CLI:           ``--folderinbox``
:Type:          ``str``
:Default:       ``INBOX`` (This is the name for the default IMAP inbox)
:Required:      No
:Description:   Folder from which emails shall be fetched for parsing. Using the default IMAP inbox is recommended
                unless you know what you're doing.
:Example:       ``mycoolfolder``

Success
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_FOLDER_SUCCESS``
:CLI:           ``--foldersuccess``
:Type:          ``str``
:Default:       ``jicket``
:Required:      No
:Description:   Imap folder to which successfully imported emails shall be moved. The folder must exist and must not be
                the same as ``JICKET_FOLDER_INBOX``.
:Example:       ``myothercoolfolder``

Thread template
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_THREAD_TEMPLATE``
:CLI:           ``--threadtemplate``
:Type:          ``str``
:Required:      Yes
:Description:   Path to HTML file containing template for ticket thread emails. Can be absolute or relative path.
                See :doc:`threadtemplate` on how to format the template.
:Example:       ``/etc/jicket/threadtemplate.html``

Ticket Address
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_TICKET_ADDRESS``
:CLI:           ``--ticketaddress``
:Type:          ``str``
:Required:      Yes
:Description:   Email address of ticket system. This is the address your customers should contact, and from which they
                will in turn receive the ticket creation confirmation.
:Example:       ``support@example.com``



Operation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Configuration of jicket operation

Loopmode
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_LOOPMODE``
:CLI:           ``--loopmode``
:Type:          ``str``
:Default:       ``dynamic``
:Required:      No
:Description:   How the main loop shall operate.

                dynamic
                  After finishing with fetching and processing the main loop will sleep for ``JICKET_LOOPTIME`` before
                  fetching again.

                interval
                  Tries to run the main loop exactly every ``JICKET_LOOPTIME`` seconds. If main loop execution takes
                  longer than that, there is no break between subsequent executions.
:Example:       ``interval``


Looptime
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_LOOPTIME``
:CLI:           ``--looptime``
:Type:          ``float``
:Default:       ``60``
:Required:      No
:Description:   Length between loop execution. Also see ``JICKET_LOOPMODE`` how exactly this time is applied.
:Example:       ``120``



Ticket ID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Miscellaneous configuration

Prefix
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_ID_PREFIX``
:CLI:           ``--idprefix``
:Type:          ``str``
:Default:       ``JI-``
:Required:      No
:Description:   A prefix that is prepended to ticket IDs. This could for example be your company initials.
:Example:       ``EC-`` will produce ticket IDs like ``[#EC-XXXXX]``

Hash salt
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_ID_SALT``
:CLI:           ``--idsalt``
:Type:          ``str``
:Default:       ``JicketSalt``
:Required:      No
:Description:   The salt for hashing ticket IDs. Only needs to be set if you don't want your users to be able to find
                out the true ID of the ticket (which is the email's UID).
:Example:       ``VerySecretSalt``

Hash alphabet
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_ID_ALPHABET``
:CLI:           ``--idalphabet``
:Type:          ``str``
:Default:       ``ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890``
:Required:      No
:Description:   Alphabet for hashing. The generated hash will only consist of letters from this alphabet.
:Example:       ``ABCD1234``

Hash minimum length
""""""""""""""""""""""""""""""""""
:Environment:   ``JICKET_ID_ALPHABET``
:CLI:           ``--idalphabet``
:Type:          ``int``
:Default:       ``6``
:Required:      No
:Description:   Minimum length of generated hash. If the email uid is low, a hash might consist of only one character if
                no minimum length is set. Must be positive or zero.
:Example:       ``0``
