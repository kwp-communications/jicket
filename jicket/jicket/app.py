"""
Main Jicket application
"""

import argparse
from pathlib import Path
import os
import time

import jicket.log as log
import jicket.mailhandling as mailhandling
import jicket.jiraintegration as jiraintegration
from jicket.mailfilter import MailFilter

from typing import List, Tuple


class LoopHandler():
    def __init__(self, looptime: int=10):
        self.looptime = looptime    # type: int
        self.lastExecuted = 0       # type: float
        self.firstExecution = True
        self.continuerunning = True

    def tick(self) -> bool:
        pass


class DynamicLoop(LoopHandler):
    def tick(self) -> bool:
        if self.firstExecution:     # Skip sleep on first execution
            self.firstExecution = False
            return True
        time.sleep(self.looptime)
        return True


class IntervalLoop(LoopHandler):
    def tick(self) -> bool:
        if time.time() > (self.lastExecuted + self.looptime):
            self.lastExecuted = time.time()
            time.sleep(1)
            return True
        else:
            return False

class Singleshot(LoopHandler):
    def tick(self) -> bool:
        self.continuerunning = False
        return True


def argparse_env(varname, default=None):
    """Helper function for fetching environment variables in argparse

    This function fetches an environment variable, which is returned as the default value for the argument. If no
    environment variable is found, and no default value is set, the argument is instead set to required.

    Usage: parser.add_argument("--foo", **argparse_env(varname, default))"""
    if os.getenv(varname, default) is not None:
        return {"default": os.getenv(varname, default), "metavar": varname}
    else:
        return {"required": True, "metavar": varname}


class JicketApp():
    def __init__(self):
        self.args: argparse.Namespace = None

    def parse_arguments(self):
        parser = argparse.ArgumentParser("Jicket - Jira Email Ticket System")

        parser.add_argument("--imaphost", type=str, help="Host URL of IMAP mailbox", **argparse_env("JICKET_IMAP_HOST"))
        parser.add_argument("--imapport", type=int, help="Port of IMAP host", **argparse_env("JICKET_IMAP_PORT", 993))
        parser.add_argument("--imapuser", type=str, help="User for IMAP", **argparse_env("JICKET_IMAP_USER"))
        parser.add_argument("--imappass", type=str, help="Password for IMAP", **argparse_env("JICKET_IMAP_PASS"))

        parser.add_argument("--smtphost", type=str, help="Host URL of SMTP server", **argparse_env("JICKET_SMTP_HOST"))
        parser.add_argument("--smtpport", type=int, help="Port of SMTP host", **argparse_env("JICKET_SMTP_PORT", 587))
        parser.add_argument("--smtpuser", type=str, help="User for SMTP (If left empty, IMAP user is used)",
                            **argparse_env("JICKET_SMTP_USER", ""))
        parser.add_argument("--smtppass", type=str, help="Password for SMTP (If left empty, IMAP pass is used)",
                            **argparse_env("JICKET_SMTP_PASS", ""))

        parser.add_argument("--jiraurl", type=str, help="URL of JIRA instance", **argparse_env("JICKET_JIRA_URL"))
        parser.add_argument("--jirauser", type=str, help="User for JIRA instance", **argparse_env("JICKET_JIRA_USER"))
        parser.add_argument("--jirapass", type=str, help="Password for JIRA user", **argparse_env("JICKET_JIRA_PASS"))
        parser.add_argument("--jiraproject", type=str, help="Project to which tickets shall be added",
                            **argparse_env("JICKET_JIRA_PROJECT"))

        parser.add_argument("--folderinbox", type=str, help="Folder from which to read incoming mails",
                            **argparse_env("JICKET_FOLDER_INBOX", "INBOX"))
        parser.add_argument("--foldersuccess", type=str,
                            help="Folder in which successfully imported mails are put",
                            **argparse_env("JICKET_FOLDER_SUCCESS", "jicket"))
        parser.add_argument("--threadtemplate", type=str,
                            help="Folder in which successfully imported mails are put",
                            **argparse_env("JICKET_THREAD_TEMPLATE"))

        parser.add_argument("--ticketaddress", type=str, help="Email-address of Helpdesk",
                            **argparse_env("JICKET_TICKET_ADDRESS"))
        parser.add_argument("--filterconfig", type=str,
                            help="Path to file containing filter config, if any",
                            **argparse_env("JICKET_FILTER_CONFIG", ""))

        parser.add_argument("--idprefix", type=str, help="Prefix for ticket IDs",
                            **argparse_env("JICKET_ID_PREFIX", "JI-"))
        parser.add_argument("--idsalt", type=str, help="Salt for ticket ID hashing",
                            **argparse_env("JICKET_ID_SALT", "JicketSalt"))
        parser.add_argument("--idalphabet", type=str, help="Alphabet for ticket ID hashing",
                            **argparse_env("JICKET_ID_ALPHABET", "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        parser.add_argument("--idminlen", type=int, help="Minimum character length of ID hash",
                            **argparse_env("JICKET_ID_MINLEN", 6))

        parser.add_argument("--loopmode", type=str, help="Loop Mode", **argparse_env("JICKET_LOOPMODE", "dynamic"))
        parser.add_argument("--looptime", type=int, help="Time between imap reads in seconds",
                            **argparse_env("JICKET_LOOPTIME", 60))

        self.args = parser.parse_args()

    def populate_config(self):
        self.mailconf: MailConfig = mailhandling.MailConfig()
        self.jiraconf: JiraConfig = jiraintegration.JiraConfig()

        self.mailconf.IMAPHost = self.args.imaphost
        self.mailconf.IMAPPort = self.args.imapport
        self.mailconf.IMAPUser = self.args.imapuser
        self.mailconf.IMAPPass = self.args.imappass

        self.mailconf.SMTPHost = self.args.smtphost
        self.mailconf.SMTPPort = self.args.smtpport
        self.mailconf.SMTPUser = self.args.smtpuser
        self.mailconf.SMTPPass = self.args.smtppass
        if self.mailconf.SMTPUser == "":
            self.mailconf.SMTPUser = self.mailconf.IMAPUser
        if self.mailconf.SMTPPass == "":
            self.mailconf.SMTPPass = self.mailconf.IMAPPass

        self.jiraconf.jiraHost = self.args.jiraurl
        self.jiraconf.jiraUser = self.args.jirauser
        self.jiraconf.jiraPass = self.args.jirapass
        self.jiraconf.project = self.args.jiraproject

        self.mailconf.folderInbox = self.args.folderinbox
        self.mailconf.folderSuccess = self.args.foldersuccess
        self.mailconf.threadStartTemplate = Path(self.args.threadtemplate)

        self.mailconf.ticketAddress = self.args.ticketaddress

        self.mailconf.idPrefix = self.args.idprefix
        self.mailconf.idSalt = self.args.idsalt
        self.mailconf.idAlphabet = self.args.idalphabet
        self.mailconf.idMinLength = self.args.idminlen

        if self.mailconf.checkValidity():
            log.success("Email configuration valid")

    def check_available_mails(self) -> List[int]:
        """Check how many mails are available in the inbox

        Returns:
            List of email uids that are to be processed
        """
        pass

    def process_mail(self, uid: int) -> bool:
        """process a single mail from currently available mails

        Args:
            uid: uid of email that shall be processed

        Returns:
            Success of processing
        """
        pass
