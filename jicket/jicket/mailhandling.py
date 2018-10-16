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
import hashids
import re

from pathlib import Path

class MailConfig():
    """Configuration for MailImporter"""
    def __init__(self):
        self.IMAPHost = None    # type: str
        self.IMAPPort = 993     # type: int
        self.IMAPUser = None    # type: str
        self.IMAPPass = None    # type: str

        self.SMTPHost = None    # type: str
        self.SMTPPort = 587     # type: int
        self.SMTPUser = None    # type: str
        self.SMTPPass = None    # Type: str

        self.folderInbox = "INBOX"    # type: str               # Folder from which incoming messages are retrieved
        self.folderSuccess = "jicket-incoming"    # type: str   # Where mails shall be put after import
        self.threadStartTemplate = Path("threadtemplate.html")  # type: Path

        self.ticketAddress = None       # type: str # Address of jicket mailbox

        self.idPrefix = "JI-"    # type: str
        self.idSalt = "JicketSalt"  # type: str
        self.idAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"    # type: str
        self.idMinLength = 6    # type: int

    def checkValidity(self) -> bool:
        """Checks if configuration parameters are valid"""
        log.warning("Mail config validity check not yet implemented!")
        return True

class ProcessedMail():
    def __init__(self, uid: int, rawmailcontent: bytes, config: MailConfig):
        self.uid = uid  # type: int # Email UID from mailbox. See RFC3501 2.3.1.1.
        self.rawmailcontent = rawmailcontent    # type: bytes
        self.config = config

        self.body = ""  # type: str
        self.parsed = None  # type: email.message.Message
        self.ticketid = None    # type: int # ID of ticket
        self.tickethash = None  # type: str # Hashed ticket ID
        self.prefixedhash = None    # type: str # Hashed ticket ID with prefix

        self.threadstarter = False

        self.process()
        self.determineTicketID()

    def process(self) -> None:
        """Parse email and fetch body and all attachments"""
        self.parsed = email.message_from_bytes(self.rawmailcontent) # type: email.message.EmailMessage

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
        recipients = mail["To"].split(",")
        if mail["CC"]:
            recipients += mail["CC"].split(",")
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
        threadstarter["To"] = "%s, %s" % (mail.parsed["From"], self.mailconfig.ticketAddress)
        threadstarter["CC"] = mail.parsed["CC"]
        threadstarter["From"] = self.mailconfig.ticketAddress
        threadstarter["In-Reply-To"] = mail.parsed["Message-ID"].rstrip().lstrip()
        threadstarter["Subject"] = "[#%s%s] %s" % (self.mailconfig.idPrefix, mail.tickethash, mail.subject)

        # Send mail
        self.sendmail(threadstarter)
