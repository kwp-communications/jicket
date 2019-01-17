import unittest

from jicket.mailhandling import MailConfig
from pathlib import Path


class MailConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.setUpConfig1()
        self.setUpConfig2()

    def setUpConfig1(self):
        self.config1 = MailConfig()
        self.config1.IMAPHost = None  # type: str
        self.config1.IMAPPort = 993  # type: int
        self.config1.IMAPUser = None  # type: str
        self.config1.IMAPPass = None  # type: str

        self.config1.SMTPHost = None  # type: str
        self.config1.SMTPPort = 587  # type: int
        self.config1.SMTPUser = None  # type: str
        self.config1.SMTPPass = None  # Type: str

        self.config1.folderInbox = "INBOX"  # type: str               # Folder from which incoming messages are retrieved
        self.config1.folderSuccess = "jicket-incoming"  # type: str   # Where mails shall be put after import
        self.config1.threadStartTemplate = Path("threadtemplate.html")  # type: Path

        self.config1.ticketAddress = "foo@bar.baz"  # type: str # Address of jicket mailbox

        self.config1.idPrefix = "JI-"  # type: str
        self.config1.idSalt = "JicketSalt"  # type: str
        self.config1.idAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"  # type: str
        self.config1.idMinLength = 6  # type: int

    def test_invalid_address(self):
        """Check if the ticketAddress is correctly validated"""
        self.assertTrue(self.config1.checkValidity())

        self.config1.ticketAddress = "foobar.baz"
        #self.assertFalse(self.config1.checkValidity())

        self.config1.ticketAddress = "foo@bar"
        #self.assertFalse(self.config1.checkValidity())

    def setUpConfig2(self):
        self.config2 = MailConfig()
        self.config2.IMAPHost = None  # type: str
        self.config2.IMAPPort = 993  # type: int
        self.config2.IMAPUser = None  # type: str
        self.config2.IMAPPass = None  # type: str

        self.config2.SMTPHost = None  # type: str
        self.config2.SMTPPort = 587  # type: int
        self.config2.SMTPUser = None  # type: str
        self.config2.SMTPPass = None  # Type: str

        self.config2.folderInbox = "INBOX"  # type: str               # Folder from which incoming messages are retrieved
        self.config2.folderSuccess = "jicket-incoming"  # type: str   # Where mails shall be put after import
        self.config2.threadStartTemplate = Path("threadtemplate.html")  # type: Path

        self.config2.ticketAddress = "foo@bar.baz"  # type: str # Address of jicket mailbox

        self.config2.idPrefix = "JI-"  # type: str
        self.config2.idSalt = "JicketSalt"  # type: str
        self.config2.idAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"  # type: str
        self.config2.idMinLength = 6  # type: int

    def test_invalid_idlen(self):
        """Check if the idMinLength field is correctly validated"""

        self.config2.idMinLength = 6    # Default value
        self.assertTrue(self.config2.checkValidity())

        self.config2.idMinLength = 0
        self.assertTrue(self.config2.checkValidity())

        try:
            self.config2.idMinLength = -1
            self.config2.checkValidity()
        except Exception:
            pass
        else:
            self.fail("Invalid minIdLength didn't trigger exception")


if __name__ == '__main__':
    unittest.main()
