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

        self.idPrefix = "JI"    # type: str
        self.idSalt = "JicketSalt"  # type: str
        self.idAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"    # type: str
        self.idMinLength = 6    # type: int

    def checkValidity(self):
        """Checks if configuration parameters are valid"""
        pass

class ProcessedMail():
    def __init__(self, uid: int, rawmailcontent: bytes, config: MailConfig):
        self.uid = uid  # type: int # Email UID from mailbox. See RFC3501 2.3.1.1.
        self.rawmailcontent = rawmailcontent    # type: bytes
        self.config = config

        self.body = ""  # type: str
        self.parsed = None  # type: email.message.Message
        self.ticketid = None    # type: int # ID of ticket
        self.tickethash = None  # type: str # Hashed ticket ID

        self.process()
        self.determineTicketID()

    def process(self) -> None:
        """Parse email and fetch body and all attachments"""
        self.parsed = email.message_from_bytes(self.rawmailcontent) # type: email.message.EmailMessage

        if self.parsed.is_multipart():
            for part in self.parsed.get_payload():
                if part.get_content_maintype() == "text":
                    # Append all text parts together. Usually there shouldn't be more than one text part.
                    self.body += part.get_payload(decode=True).decode(part.get_content_charset())
        else:
            if self.parsed.get_content_maintype() == "text":
                self.body += self.parsed.get_payload()

        self.subject = self.parsed["subject"]
        # TODO: Get all attachments
        self.rawmailcontent = None  # No need to store after processing

    def determineTicketID(self):
        """Determine ticket id either from existing subject line or from uid

        If the Subject line contains an ID, it is taken. If it doesn't, a new one is generated.
        """
        hashid = hashids.Hashids(salt=self.config.idSalt, alphabet=self.config.idAlphabet, min_length=self.config.idMinLength)

        idregex = "\[%s-([%s]{%i,}?)\]" % (self.config.idPrefix, self.config.idAlphabet, self.config.idMinLength)
        match = re.match(idregex, self.subject)
        if match:
            self.tickethash = match.group(1)
            self.ticketid = hashid.decode(self.tickethash)
        else:
            self.tickethash = hashid.encode(self.uid)
            self.ticketid = self.uid


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
        self.SMTP.sendmail(mail["From"], mail["To"], mail.as_string())

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

        # Set other headers
        threadstarter["To"] = "%s, %s" % (mail.parsed["From"], self.mailconfig.ticketAddress)
        threadstarter["From"] = self.mailconfig.ticketAddress
        threadstarter["In-Reply-To"] = mail.parsed["Message-ID"].rstrip()
        threadstarter["Subject"] = "[#%s] %s" % (mail.tickethash, mail.subject)

        # Send mail
        self.sendmail(threadstarter)
