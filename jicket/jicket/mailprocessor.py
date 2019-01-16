from typing import Union, List
import imaplib
import smtplib
import ssl
import jicket.log as log
import email.parser
import email.mime.text
import email.headerregistry
import email.policy
import hashids
import re
from jicket.config import MailConfig

class ProcessedMail():
    def __init__(self, uid: int, rawmailcontent: bytes, config: MailConfig):
        self.uid: int = uid     # Email UID from mailbox. See RFC3501 2.3.1.1.
        self.rawmailcontent: bytes = rawmailcontent     # Email as it comes from IMAP server
        self.config = config

        self.parsed: email.message.Message = None   # parsed email object
        self.ticketid: int = None       # ID of ticket
        self.tickethash: str = None     # Hashed ticket ID
        self.prefixedhash: str = None   # Hashed ticket ID with prefix

        self.threadstarter: bool = False  # Whether mail is threadstarter

        self.process()
        self.determineTicketID()

    def process(self) -> None:
        """Parse email and fetch body and all attachments"""
        self.parsed = email.message_from_bytes(self.rawmailcontent, policy=email.policy.EmailPolicy())    # type: email.message.EmailMessage

        self.subject = self.parsed["subject"]

        if self.parsed["X-Jicket-Initial-ReplyID"] is not None and self.parsed["X-Jicket-Initial-ReplyID"] == self.parsed["In-Reply-To"]:
            self.threadstarter = True
        elif self.config.ticketAddress in self.parsed["From"]:  # Take more heuristic approach
            self.threadstarter = True

        self.rawmailcontent = None  # No need to store after processing

    def determineTicketID(self):
        """Determine ticket id either from existing subject line or from uid

        If the Subject line contains an ID, it is taken. If it doesn't, a new one is generated.
        """
        hashid = hashids.Hashids(salt=self.config.idSalt, alphabet=self.config.idAlphabet, min_length=self.config.idMinLength)

        # See if hashid is set in headers
        if self.parsed["X-Jicket-HashID"] is not None:
            self.tickethash = self.parsed["X-Jicket-HashID"]
            self.ticketid = hashid.decode(self.parsed["X-Jicket-HashID"])
        else:
            idregex = "\\[#%s([%s]{%i,}?)\\]" % (re.escape(self.config.idPrefix), re.escape(self.config.idAlphabet), self.config.idMinLength)
            match = re.search(idregex, self.subject)
            if match:
                self.tickethash = match.group(1)
                self.ticketid = hashid.decode(self.tickethash)
            else:
                self.tickethash = hashid.encode(self.uid)
                self.ticketid = self.uid

        self.prefixedhash = self.config.idPrefix + self.tickethash
