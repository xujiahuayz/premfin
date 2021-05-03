from dataclasses import dataclass
import pandas as pd
import numpy as np
from os import path
from typing import Optional

from premiumFinance.mortality import Mortality


@dataclass
class Insured:
    issue_age: int
    current_age: Optional[int]
    isMale: bool = True
    isSmoker: Optional[bool] = False
    issuemort: float = 1
    currentmort: float = 1
    issueVBT: str = "VBT01"
    currentVBT: str = "VBT15"

    def __post_init__(self):
        if self.current_age is None:
            self.current_age = self.issue_age
        assert (
            self.issue_age <= self.current_age
        ), "Issue age must not exceed current age"

    @property
    def mortality_at_issue(self):
        im = Mortality(
            issueage=self.issue_age,
            currentage=self.issue_age,  # currentage = issueage at policy issuance
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=self.issuemort,
            whichVBT=self.issueVBT,
        )
        return im

    @property
    def currentMort(self):
        cm = Mortality(
            issueage=self.issue_age,
            currentage=self.current_age,
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=self.currentmort,
            whichVBT=self.currentVBT,
        )
        return cm
