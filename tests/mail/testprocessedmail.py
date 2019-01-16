import unittest
from jicket.mailhandling import ProcessedMail, MailConfig
from pathlib import Path

class ProcessedMailTestCase(unittest.TestCase):
    def setUpMailConfig(self):
        self.config = MailConfig()
        self.config.IMAPHost = None  # type: str
        self.config.IMAPPort = 993  # type: int
        self.config.IMAPUser = None  # type: str
        self.config.IMAPPass = None  # type: str

        self.config.SMTPHost = None  # type: str
        self.config.SMTPPort = 587  # type: int
        self.config.SMTPUser = None  # type: str
        self.config.SMTPPass = None  # Type: str

        self.config.folderInbox = "INBOX"  # type: str               # Folder from which incoming messages are retrieved
        self.config.folderSuccess = "jicket-incoming"  # type: str   # Where mails shall be put after import
        self.config.threadStartTemplate = Path("threadtemplate.html")  # type: Path

        self.config.ticketAddress = "ticket-test@kwp-communications.com"  # type: str # Address of jicket mailbox

        self.config.idPrefix = "JI-"  # type: str
        self.config.idSalt = "JicketSalt"  # type: str
        self.config.idAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"  # type: str
        self.config.idMinLength = 6  # type: int

    def setUp(self):
        self.setUpMailConfig()

        path = Path(__file__).parent / "data/threadstarter.eml"
        with path.open("rb") as f:
            self.threadstarter = f.read()
            self.processed_threadstarter = ProcessedMail(-1, self.threadstarter, self.config)

    def test_threadstarter(self):
        """"""
        # Because the ticketid isn't -1, it means that it was recovered from the email. A negative ID would be
        # impossible, because IMAP starts counting uids up from 0, and the ticket id is just the email's imap uid.
        print("Ticket ID: %i" % self.processed_threadstarter.ticketid)
        self.assertTrue(self.processed_threadstarter.ticketid != -1)

        # Check if prefix is applied correctly
        print("Ticket Hash: %s" % self.processed_threadstarter.tickethash)
        print("ID prefix: %s" % self.config.idPrefix)
        print("Constructed Prefixed Hash: %s%s" % (self.config.idPrefix, self.processed_threadstarter.tickethash))
        print("Actual Prefixed Hash: %s" % self.processed_threadstarter.prefixedhash)
        self.assertTrue("%s%s" % (
            self.config.idPrefix, self.processed_threadstarter.tickethash) == self.processed_threadstarter.prefixedhash)

        # Check if email was correctly identified as a threadstarter
        print("Email is Threadstarter: %s" % self.processed_threadstarter.threadstarter)
        self.assertTrue(self.processed_threadstarter.threadstarter)

    def test_transferencoding(self):
        path = Path(__file__).parent / "data/transferencoding/threadstarter.eml"
        with path.open("rb") as f:
            threadstarter = f.read()
            processed_threadstarter = ProcessedMail(-1, self.threadstarter, self.config)

        path = Path(__file__).parent / "data/transferencoding/threadstarter_decoded.html"
        with path.open("r") as f:
            decoded_body = f.read()


