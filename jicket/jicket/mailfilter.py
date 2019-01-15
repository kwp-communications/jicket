from jicket.mailhandling import ProcessedMail

import re
import json
from pathlib import Path

from typing import Tuple, List


class FilterRule():
    def __init__(self, config: dict):
        self.addresspattern = None
        self.subjectpattern = None
        self.description = "NO DESCRIPTION GIVEN"
        self.ignorecase = False
        if "addresspattern" in config:
            self.addresspattern: str = config["addresspattern"]
        if "subjectpattern" in config:
            self.subjectpattern: str = config["subjectpattern"]
        if "description" in config:
            self.description = config["description"]
        if "ignorecase" in config:
            self.ignorecase = config["ignorecase"]

    def filtermail(self, mail: ProcessedMail) -> bool:
        """

        :param mail: Mail to be checked
        :return: Returns whether the filter has a positive match
        :rtype: bool
        """
        reflags = 0
        if self.ignorecase:
            reflags = reflags | re.IGNORECASE
        if self.subjectpattern is not None and re.search(self.subjectpattern, mail.subject, reflags):
            return True
        if self.addresspattern is not None and re.search(self.addresspattern, mail.parsed["from"], reflags):
            return True
        return False


class BlacklistFilterRule(FilterRule):
    pass


class WhitelistFilterRule(FilterRule):
    pass


class MailFilter():
    def __init__(self, filterpath: Path):
        with filterpath.open("r") as f:
            config = json.load(f)

        self.blacklist = []
        for blconfig in config["blacklist"]:
            self.blacklist.append(BlacklistFilterRule(blconfig))

        self.whitelist = []
        for wlconfig in config["whitelist"]:
            self.whitelist.append(WhitelistFilterRule(wlconfig))

    def filtermail(self, mail: ProcessedMail) -> Tuple[bool, List[str]]:
        filtered: bool = False
        description: List[str] = []
        for blacklistfilter in self.blacklist:
            if blacklistfilter.filtermail(mail):
                filtered = True
                description.append("BLACKLISTED: %s" % blacklistfilter.description)

        if filtered:
            for whitelistfilter in self.whitelist:
                if whitelistfilter.filtermail(mail):
                    filtered = False
                    description.append("WHITELISTED: %s" % whitelistfilter.description)

        return (filtered, description)
