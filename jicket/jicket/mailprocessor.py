from typing import Union, List, Dict
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

import html2text

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

        self.textbodies: Dict[str, str] = {}    # All text bodies found in email. Key is maintype, value is content.

        self.process()
        self.determine_ticket_ID()

    def process(self) -> None:
        """Parse email and fetch body and all attachments"""
        self.parsed = email.message_from_bytes(self.rawmailcontent, policy=email.policy.EmailPolicy())    # type: email.message.EmailMessage

        self.subject = self.parsed["subject"]

        if self.parsed["X-Jicket-Initial-ReplyID"] is not None and self.parsed["X-Jicket-Initial-ReplyID"] == self.parsed["In-Reply-To"]:
            self.threadstarter = True
        elif self.config.ticketAddress in self.parsed["From"]:  # Take more heuristic approach
            self.threadstarter = True

        self.rawmailcontent = None  # No need to store after processing

        self.get_text_bodies(self.parsed)
        self.textfrombodies()

    def determine_ticket_ID(self):
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

    def get_text_bodies(self, startpart):
        if startpart.is_multipart():
            for part in startpart.get_payload():
                if part.is_multipart():
                    self.get_text_bodies(part)
                elif part.get_content_maintype() == "text":
                    if part.get_content_charset() is not None:
                        self.textbodies[part.get_content_subtype()] = part.get_payload(decode=True).decode(part.get_content_charset())
                    else:
                        # If no charset is provided, assume UTF-8 as per RFC 6657
                        self.textbodies[part.get_content_subtype()] = part.get_payload(decode=True).decode("utf-8")
        else:
            self.textbodies[self.parsed.get_content_subtype()] = startpart.get_payload(
                decode=True).decode(self.parsed.get_content_charset())

    def textfrombodies(self) -> str:
        """Convert text bodies to text that can be attached to an issue"""
        type_priority = ["plain", "html", "other"]  # TODO: Make configurable

        for texttype in type_priority:
            if texttype == "plain" and texttype in self.textbodies:
                """Text is plain, so it can be used verbatim"""
                return self.textbodies[texttype]
            if texttype == "html" and texttype in self.textbodies:
                """HTML text. Convert to markup with html2text and remove extra spaces"""
                text = html2text.html2text(self.textbodies[texttype])
                # Remove every second newline which is added to distinguish between paragraphs in Markdown, but makes
                # the jira ticket hard to read.
                return re.sub("(\n.*?)\n", "\g<1>", text)
            if texttype == "other" and len(self.textbodies):
                # If no other text is found, return the first available body if any.
                return self.textbodies[list(self.textbodies.keys())[0]]
        return "The email contained no text bodies."
