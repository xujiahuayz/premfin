from dataclasses import dataclass
import pandas as pd
import numpy as np
from os import path
from typing import Optional

from premiumFinance.mortality import Mortality


@dataclass
class Insured:
    issueage: int
    isMale: bool
    isSmoker: Optional[bool]
    currentage: Optional[int]
    issuemort: float = 1
    currentmort: float = 1
    issueVBT: str = "VBT01"
    currentVBT: str = "VBT15"

    def __post_init__(self):
        if self.currentage is None:
            self.currentage = self.issueage
        assert self.issueage <= self.currentage, "Issue age must not exceed current age"

    def issueMort(self):
        im = Mortality(
            issueage=self.issueage,
            currentage=self.issueage,  # currentage = issueage at policy issuance
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=self.issuemort,
            whichVBT=self.issueVBT,
        )
        return im

    def currentMort(self):
        cm = Mortality(
            issueage=self.issueage,
            currentage=self.currentage,
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=self.currentmort,
            whichVBT=self.currentVBT,
        )
        return cm
