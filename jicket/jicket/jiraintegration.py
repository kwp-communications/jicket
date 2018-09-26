"""Creates or updates issue from Mail"""

from typing import List, Tuple
from jicket.mailhandling import ProcessedMail
import jira
import jicket.log as log
import html2text
import re

class JiraConfig():
    def __init__(self):
        self.jiraHost = None    # type: str
        self.jiraUser = None    # type: str
        self.jiraPass = None    # type: str
        self.project = None   # type: str

    def checkValidity(self) -> bool:
        """Checks if configuration parameters are valid"""
        log.warning("Jira config validity check not yet implemented!")
        return True


class JiraIntegration():
    def __init__(self, mail: ProcessedMail, config: JiraConfig):
        self.mail = mail    # type: ProcessedMail
        self.config = config    # type: JiraConfig

        self.jira = jira.JIRA(self.config.jiraHost, basic_auth=(self.config.jiraUser, self.config.jiraPass))


    def processMail(self) -> Tuple[bool, bool]:
        """Updates or creates new issue from mail

        :returns: Tuple[bool, bool] Tuple indicating the jira import success and if this is a new issue"""
        issues = self.findIssue()
        try:
            if issues:
                for issue in issues:
                    self.updateIssue(issue)
                return (True, False)
            else:
                self.newIssue()
                return (True, True)
        except jira.exceptions.JIRAError:
            return False, False


    def findIssue(self) -> List[jira.Issue]:
        """Check if issue for ticketid exists already"""
        issues = self.jira.search_issues("project = %s AND summary~'\\\\[\\\\#%s\\\\]'" % (self.config.project, self.mail.prefixedhash))

        return issues


    def newIssue(self):
        """Create a new issue from Mail"""
        log.info("Creating new Issue for #%s in project %s" % (self.mail.prefixedhash, self.config.project))

        # Construct string for description
        description = ""
        description += "Imported by Jicket (SequentialID: %i)" % self.mail.ticketid
        description += "From: %s\n\n\n" % self.mail.parsed["From"]
        description += re.sub("(\n.*?)\n", "\g<1>", html2text.html2text(self.mail.body))    # Remove every second newline which is added to distinguish between paragraphs in Markdown, but makes the jira ticket hard to read.

        issuedict = {
            "project": {"key": self.config.project},
            "summary": "[#%s] %s" % (self.mail.prefixedhash, self.mail.subject),
            "description": description,
            "issuetype": {"name": "Task"}
        }

        self.jira.create_issue(fields=issuedict)


    def updateIssue(self, issue: jira.Issue):
        """Update issue from mail"""
        log.info("Updating Issue for #%s in project %s" % (self.mail.prefixedhash, self.config.project))

        commenttext = ""
        commenttext += "From: %s\n\n\n" % self.mail.parsed["From"]
        commenttext += re.sub("(\n.*?)\n", "\g<1>", html2text.html2text(self.mail.body))

        comment = self.jira.add_comment(issue, commenttext)     # TODO: error checking
