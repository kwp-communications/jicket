"""Configuration classes used by other classes"""

import re
from pathlib import Path


class MailConfig():
    """Configuration for MailImporter"""

    def __init__(self):
        self.IMAPHost = None  # type: str
        self.IMAPPort = 993  # type: int
        self.IMAPUser = None  # type: str
        self.IMAPPass = None  # type: str

        self.SMTPHost = None  # type: str
        self.SMTPPort = 587  # type: int
        self.SMTPUser = None  # type: str
        self.SMTPPass = None  # Type: str

        self.folderInbox = "INBOX"  # type: str               # Folder from which incoming messages are retrieved
        self.folderSuccess = "jicket-incoming"  # type: str   # Where mails shall be put after import
        self.threadStartTemplate = Path("threadtemplate.html")  # type: Path

        self.ticketAddress = None  # type: str # Address of jicket mailbox

        self.idPrefix = "JI-"  # type: str
        self.idSalt = "JicketSalt"  # type: str
        self.idAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"  # type: str
        self.idMinLength = 6  # type: int

    def checkValidity(self) -> bool:
        """Checks if configuration parameters are valid"""
        match = re.match("[^@\s]+@[^@\s]+\.[^@\s]+", self.ticketAddress)
        if not match:
            raise Exception("Ticket address must be in format: aaaa@bbbb.cc (is: %s)" % self.ticketAddress)

        if self.idMinLength < 0:
            raise Exception("Minimum ID length must be 0 or greater (is: %s)" % self.idMinLength)

        return True


class JiraConfig():
    def __init__(self):
        self.jiraHost: str = None  # Host URL of Jira
        self.jiraUser: str = None  # User for logging in
        self.jiraPass: str = None  # Pass for user
        self.project: str = None  # Project under which issues shall be added
