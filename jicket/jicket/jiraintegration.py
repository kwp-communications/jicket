"""Creates or updates issue from Mail"""

from typing import List
from jicket.mailimporter import ProcessedMail
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


class JiraIntegration():
    def __init__(self, mail: ProcessedMail, config: JiraConfig):
        self.mail = mail    # type: ProcessedMail
        self.config = config    # type: JiraConfig

        self.jira = jira.JIRA(self.config.jiraHost, basic_auth=(self.config.jiraUser, self.config.jiraPass))

        self.processMail()


    def processMail(self) -> None:
        issues = self.findIssue()
        if issues:
            for issue in issues:
                self.updateIssue(issue)
        else:
            self.newIssue()


    def findIssue(self) -> List[jira.Issue]:
        """Check if issue for ticketid exists already"""
        issues = self.jira.search_issues("project = %s AND summary~'\\\\[\\\\#%s\\\\]'" % (self.config.project, self.mail.tickethash))

        return issues


    def newIssue(self):
        """Create a new issue from Mail"""
        log.info("Creating new Issue for #%s in project %s" % (self.mail.tickethash, self.config.project))

        # Construct string for description
        description = ""
        description += "Imported by Jicket (SequentialID: %i)\n\n\n" % self.mail.ticketid
        description += re.sub("(\n.*?)\n", "\g<1>", html2text.html2text(self.mail.body))
        with open("mail.md", "w") as f:
            f.write(html2text.html2text(self.mail.body))

        issuedict = {
            "project": {"key": self.config.project},
            "summary": "[#%s] %s" % (self.mail.tickethash, self.mail.subject),
            "description": description,
            "issuetype": {"name": "Task"}
        }

        self.jira.create_issue(fields=issuedict)


    def updateIssue(self, issue: jira.Issue):
        """Update issue from mail"""
        log.info("Updating Issue for #%s in project %s" % (self.mail.tickethash, self.config.project))

        commenttext = ""
        commenttext += "Imported by Jicket (SequentialID: %i)\n\n\n" % self.mail.ticketid
        commenttext += re.sub("(\n.*?)\n", "\g<1>", html2text.html2text(self.mail.body))

        comment = self.jira.add_comment(issue, commenttext)     # TODO: error checking
