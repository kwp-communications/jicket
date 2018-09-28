Overview
==================================
The goal of jicket was to create a stateless email importer to turn a Jira issue board into a very simple service
helpdesk. Stateless means that all necessary information for operating is inferred from the emails themselves
and Jira. This makes updating or migrating your jicket instance very easy, as you don't have to migrate any state data.

Ticket process
----------------------------------
Jicket is continuously monitoring a mailbox for incoming emails. It parses those emails and then processes the email
depending on the content. If the processing and subsequent import in Jira was successful, the email is moved into a
specified folder from where on your service staff can interact with them.

When a mail is processed, jicket checks if the subject contains a ``X-Jicket-HashID`` header or if the subject line
contains a ticket ID. If it does, the email is imported as a reply to an existing issue. If not, a new issue is created
from the email.


New issue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When an email is identified as a new communication, jicket generates a new ticket ID and adds a new issue to the
configured project. To confirm the creation of the ticket, an email is sent out to the customer and the ticket address
which is meant to start an email thread. Also included is a modified subject which contains the ticket ID for this
issue.

An example conversation could look like this:
::
    Feature XY broken                                       Customer <foo@customer.com>
    ├── [#JI-ZOZ2P6] Feature XY broken                      Jicket <support@company.com>
    │   ├── RE: [#JI-ZOZ2P6] Feature XY broken              Fred Bobber <f.bobber@company.com>
    │   │   ├── RE: RE: [#JI-ZOZ2P6] Feature XY broken      Customer <foo@customer.com>
    │   │   ├── RE: RE: [#JI-ZOZ2P6] Feature XY broken      Samantha Else <s.else@company.com>



Reply to existing Issue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the email is identified as a reply to an existing issue, a comment with the email's content is added to the issue.
No further confirmation is sent to the customer.
