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


class LoopHandler():
    def __init__(self, looptime: int=10):
        self.looptime = looptime    # type: int
        self.lastExecuted = 0       # type: float
        self.firstExecution = True

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


def argparse_env(varname, default=None):
    """Helper function for fetching environment variables in argparse

    This function fetches an environment variable, which is returned as the default value for the argument. If no
    environment variable is found, and no default value is set, the argument is instead set to required.

    Usage: parser.add_argument("--foo", **argparse_env(varname, default))"""
    if os.getenv(varname, default) is not None:
        return {"default": os.getenv(varname, default), "metavar": varname}
    else:
        return {"required": True, "metavar": varname}


def jicketapp():
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

    args = parser.parse_args()

    mailconf = mailhandling.MailConfig()
    jiraconf = jiraintegration.JiraConfig()

    mailconf.IMAPHost = args.imaphost
    mailconf.IMAPPort = args.imapport
    mailconf.IMAPUser = args.imapuser
    mailconf.IMAPPass = args.imappass

    mailconf.SMTPHost = args.smtphost
    mailconf.SMTPPort = args.smtpport
    mailconf.SMTPUser = args.smtpuser
    mailconf.SMTPPass = args.smtppass
    if mailconf.SMTPUser == "":
        mailconf.SMTPUser = mailconf.IMAPUser
    if mailconf.SMTPPass == "":
        mailconf.SMTPPass = mailconf.IMAPPass

    jiraconf.jiraHost = args.jiraurl
    jiraconf.jiraUser = args.jirauser
    jiraconf.jiraPass = args.jirapass
    jiraconf.project = args.jiraproject

    mailconf.folderInbox = args.folderinbox
    mailconf.folderSuccess = args.foldersuccess
    mailconf.threadStartTemplate = Path(args.threadtemplate)

    mailconf.ticketAddress = args.ticketaddress

    mailconf.idPrefix = args.idprefix
    mailconf.idSalt = args.idsalt
    mailconf.idAlphabet = args.idalphabet
    mailconf.idMinLength = args.idminlen

    if mailconf.checkValidity():
        log.success("Email configuration valid")
    if mailconf.checkValidity():
        log.success("Jira configuration valid")

    loopmodes = ["dynamic", "interval"]
    if args.loopmode not in loopmodes:
        raise ValueError("Invalid loopmode: %s (Allowed values: %s)" % (args.loopmode, loopmodes))

    loophandler = None
    if args.loopmode == "dynamic":
        loophandler = DynamicLoop(args.looptime)
    if args.loopmode == "interval":
        loophandler = IntervalLoop(args.looptime)

    mailimporter = mailhandling.MailImporter(mailconf)

    log.success("Initialization successful")
    log.info("Beginning main loop")

    # Enter main loop
    while True:
        if loophandler.tick():
            newissues = False
            # Fetch new mails
            mailimporter.login()
            mails = mailimporter.fetchMails()
            mailimporter.logout()

            for mail in mails:
                # Mail is initial confirmation mail
                if mail.threadstarter:
                    mailimporter.moveImported(mail)
                    continue

                # Mail is completely new ticket or reply to ticket
                jiraint = jiraintegration.JiraIntegration(mail, jiraconf)
                success, newissue = jiraint.processMail()

                # If mail was new ticket, start a new email thread
                if newissue:
                    newissues = True
                    mailexporter = mailhandling.MailExporter(mailconf)

                    mailexporter.login()
                    mailexporter.sendTicketStart(mail)
                    mailexporter.quit()

                mailimporter.moveImported(mail)

            if newissues:
                # Fetch mails again to check if any confirmation mails were sent out which have to be moved to the
                # import success folder.
                log.info("Importing again to move confirmation mails")
                mailimporter.login()
                mails = mailimporter.fetchMails()
                mailimporter.logout()

                for mail in mails:
                    # Mail is initial confirmation mail
                    if mail.threadstarter:
                        mailimporter.moveImported(mail)
