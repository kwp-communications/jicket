"""Email Importer for Jicket

Reads all emails from a mailbox with IMAP. After the emails are parsed by jicket they will be further processed
(moved to folders for example) based on success or fail."""

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
from jicket.mailprocessor import ProcessedMail
from jicket.config import MailConfig

from pathlib import Path


def decodeheader(header: str) -> str:
    decoded = ""

    for decodedpart in email.header.decode_header(header):
        msg = decodedpart[0]
        charset = decodedpart[1]
        if charset is not None:
            decoded += bytes.decode(msg, charset)
        else:
            decoded += msg

    return decoded


class MailImporter():
    """Imports mails via IMAP4"""
    def __init__(self, mailconfig: MailConfig):
        self.mailconfig = mailconfig    # type: MailConfig
        self.IMAP = None    # type: Union[imaplib.IMAP4, imaplib.IMAP4_SSL]

        # Perform some validity checks
        self.login()
        self.checkFolders()

    def login(self):
        """Connects to the mailbox and logs in."""
        self.IMAP = imaplib.IMAP4_SSL(self.mailconfig.IMAPHost, 993, ssl_context=ssl.create_default_context())
        try:
            self.IMAP.login(self.mailconfig.IMAPUser, self.mailconfig.IMAPPass)
        except:
            log.error("IMAP login failed. Are your login credentials correct?")
            raise

    def logout(self):
        """Logs out of the mailbox and closes the connection."""
        pass

    def checkFolders(self):
        """Check if the configured folders exist"""
        log.info("Checking if configured folders exist")
        response = self.IMAP.select(self.mailconfig.folderInbox)
        if response[0] != "OK":
            log.error("Error accessing Folder '%s': %s" % (self.mailconfig.folderInbox, response[1][0].decode()))
            # TODO: Raise exception
        response = self.IMAP.select(self.mailconfig.folderSuccess)
        if response[0] != "OK":
            log.error("Error accessing Folder '%s': %s" % (self.mailconfig.folderSuccess, response[1][0].decode()))
            # TODO: Raise exception

    def fetchMails(self) -> List[ProcessedMail]:
        """Fetch mails from inbox folder and return them"""
        response = self.IMAP.select(self.mailconfig.folderInbox)
        if response[0] != "OK":
            log.error("Error accessing Folder '%s': %s" % (self.mailconfig.folderInbox, response[1][0].decode()))
            # TODO: Raise exception
        emailcount = int(response[1][0])
        if not emailcount > 0:
            return []
        log.info("%s email(s) in inbox" % emailcount)

        response = self.IMAP.uid("search", None, "(ALL)")
        if response[0] != "OK":
            log.error("Failed to retrieve mails from inbox: %s" % response[1][0].decode())
            # TODO: Raise exception?
        indices = response[1][0].split()

        mails = []
        for uid in indices:
            response = self.IMAP.uid("fetch", uid, "(RFC822)")
            if response[0] != "OK":
                log.error("Failed to fetch mail: %s" % response[1][0].decode())

            mails.append(ProcessedMail(int(uid), response[1][0][1], self.mailconfig))

        return mails

    def moveImported(self, mail):
        """Move successfully imported mails to success folder"""
        self.IMAP.uid("copy", str(mail.uid).encode(), self.mailconfig.folderSuccess)
        self.IMAP.uid("store", str(mail.uid).encode(), "+flags", "(\Deleted)")
        self.IMAP.expunge()


class MailExporter():
    """Sends out mails via SMTP"""
    def __init__(self, mailconfig: MailConfig):
        self.mailconfig = mailconfig    # type: MailConfig

    def login(self):
        self.SMTP = smtplib.SMTP(self.mailconfig.SMTPHost, self.mailconfig.SMTPPort)
        self.SMTP.ehlo()
        self.SMTP.starttls()
        self.SMTP.ehlo()
        try:
            self.SMTP.login(self.mailconfig.SMTPUser, self.mailconfig.SMTPPass)
        except smtplib.SMTPAuthenticationError:
            log.error("SMTP login failed. Are your login credentials correct?")
            raise

    def quit(self):
        self.SMTP.quit()

    def sendmail(self, mail: email.message.Message):
        recipients = []
        for addr in mail["to"].addresses:
            recipients.append(str(addr))
        if mail["cc"]:
            for addr in mail["cc"].addresses:
                recipients.append(str(addr))

        self.SMTP.sendmail(mail["From"], recipients, mail.as_string())

    def sendTicketStart(self, mail: ProcessedMail):
        """Sends the initial mail to start an email thread from an incoming email"""

        with self.mailconfig.threadStartTemplate.open("r") as f:
            responsehtml = f.read()
            responsehtml = responsehtml % {
                "ticketid": mail.tickethash,
                "subject": mail.subject
            }

        threadstarter = email.mime.text.MIMEText(responsehtml, "html")

        # Add Jicket headers
        threadstarter["X-Jicket-HashID"] = mail.tickethash
        # Initial ID this is a reply to. It is used to identify if this is a threadstarter email or regular mail.
        # Treadstarter mails should be ignored on import, as they're only of informative nature.
        threadstarter["X-Jicket-Initial-ReplyID"] = mail.parsed["Message-ID"].rstrip().lstrip()

        # Set other headers
        threadstarter["to"] = email.headerregistry.HeaderRegistry()("to", mail.parsed["from"] + ", " + self.mailconfig.ticketAddress)
        threadstarter["CC"] = mail.parsed["CC"]
        threadstarter["From"] = self.mailconfig.ticketAddress
        threadstarter["In-Reply-To"] = mail.parsed["Message-ID"].rstrip().lstrip()
        threadstarter["Subject"] = "[#%s%s] %s" % (self.mailconfig.idPrefix, mail.tickethash, mail.subject)

        # Send mail
        self.sendmail(threadstarter)
