Filtering
==================================
Jicket offers some capabilities to blacklist emails by their address and subject lines using regex patterns.
Additionally, exceptions to blacklistings can be added with a whitelist.

Filter Configuration File
----------------------------------
The filter configuration file is a JSON formatted file. The root objects contains two lists, ``blacklist`` and ``whitelist``.
Each entry in the lists is an object, consisting of the properties ``description``, ``addresspattern`` and ``subjectpattern``.


Description
^^^^^^^^^^^^^^^^^^^^
:Property:   ``description``
:Type:          ``str``
:Required:      Yes
:Description:   Description of the filter rule, which will be printed to the logs when the filter applies.
:Example:       ``Block emails matching .*@spameridoo.com for excessive spam``


Address pattern
^^^^^^^^^^^^^^^^^^^^
:Property:   ``addresspattern``
:Type:          ``str``
:Required:      No
:Description:   Python regex pattern which is matched with the address.
:Example:       ``.*@spameridoo.com``


Subject Pattern
^^^^^^^^^^^^^^^^^^^^
:Property:   ``subjectpattern``
:Type:          ``str``
:Required:      No
:Description:   Python regex pattern which is matched with the subject.
:Example:       ``buy my spam``


Ignore case
^^^^^^^^^^^^^^^^^^^^
:Property:   ``ignorecase``
:Type:          ``bool``
:Required:      No
:Description:   Whether regex shall be case insensitive
:Example:       ``true``
:Default:       ``false``


Blacklisting and Whitelisting
"""""""""""""""""""""""""""""""""""""
Each mail is matched against all available blacklist filters. If any of them matches, the mail is also checked against all whitelist filters.
If only blacklisting rules match, the mail is marked ased filtered and will not be further processed and will be moved.
If a whitelist filter matches, this mark is reset and the mail import continues as usual.


Example
"""""""""""""""""""
The following example contains a simple filter setup. The only blacklist rule filters out all emails coming from the domain ``test.com``.
However, two whitelist rules will let through emails from foo.com if they either come from ``foo@test.com``, or if the subject contains the magic keyword ``sesame``.

.. code-block:: json

    {
      "blacklist": [
        {
          "description": "Deny mails from domain test.com",
          "addresspattern": ".*@test\\.com"
        }
      ],
      "whitelist": [
        {
          "description": "Allow foo@test.com",
          "addresspattern": "foo@test\\.com"
        },
        {
          "description": "Allow because of magic word 'sesame' in subject",
          "subjectpattern": "sesame"
        }
      ]
    }