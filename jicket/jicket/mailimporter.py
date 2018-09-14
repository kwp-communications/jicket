"""Email Importer for Jicket

Reads all emails from a mailbox with IMAP. After the emails are parsed by jicket they will be further processed
(moved to folders for example) based on success or fail."""

from typing import Union
import imaplib
import ssl
import jicket.log as log

class MailConfig():
    """Configuration for MailImporter"""
    def __init__(self):
        self.IMAPHost = None    # type: str
        self.IMAPPort = 993     # type: int
        self.IMAPUser = None    # type: str
        self.IMAPPass = None    # type: str

        self.folderInbox = "INBOX"    # type: str               # Folder from which incoming messages are retrieved
        self.folderSuccess = "ticket-success"    # type: str    # Where mails shall be put on import success
        self.folderFailure = "ticket-fail"  # type: str         # Where mails shall be put in import fail


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
        self.IMAP = imaplib.IMAP4_SSL("outlook.office365.com", 993, ssl_context=ssl.create_default_context())
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
        response = self.IMAP.select(self.mailconfig.folderFailure)
        if response[0] != "OK":
            log.error("Error accessing Folder '%s': %s" % (self.mailconfig.folderFailure, response[1][0].decode()))
            # TODO: Raise exception


    def fetchMails(self):
        """Fetch mails from inbox folder and return them"""
        response = self.IMAP.select(self.mailconfig.folderInbox)
        if response[0] != "OK":
            log.error("Error accessing Folder '%s': %s" % (self.mailconfig.folderInbox, response[1][0].decode()))
            # TODO: Raise exception
        emailcount = int(response[1][0])
        if not emailcount > 0:
            return
        log.info("%s email(s) in inbox" % emailcount)

        response = self.IMAP.uid("search", None, "(ALL)")
        if response[0] != "OK":
            log.error("Failed to retrieve mails from inbox: %s" % response[1][0].decode())
            # TODO: Raise exception?
        indices = response[1][0].split()

        mails = []
        for i in indices:
            response = self.IMAP.uid("fetch", i, "(RFC822)")

            if response[0] == "OK":
                mails.append((int(i), response[1][0][1].decode()))
            else:
                log.error("Failed to fetch mail: %s" % response[1][0].decode())

        return mails
