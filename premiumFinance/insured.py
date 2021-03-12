from dataclasses import dataclass
import pandas as pd
import numpy as np
import constants
from os import path

from core import Mortality


@dataclass
class Insured:
    issueage: int
    isMale: bool
    isSmoker: bool = None
    currentage: int = None
    issuemort: float = 1
    currentmort: float = 1

    def __post_init__(self):
        if self.currentage is None:
            self.currentage = self.issueage
        assert self.issueage <= self.currentage, "Issue age must not exceed current age"

    def baseMort(self):
        bm = Mortality(
            issueage=self.issueage,
            currentage=self.currentage,
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=1,
        )
        return bm

    def issueMort(self):
        im = Mortality(
            issueage=self.issueage,
            currentage=self.issueage,  # currentage = issueage at policy issuance
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=self.issuemort,
        )
        return im

    def currentMort(self):
        cm = Mortality(
            issueage=self.issueage,
            currentage=self.currentage,
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=self.currentmort,
        )
        return cm

    def updateAge(self, age: int):
        self.currentage = age

    def updateMort(self, mort: float):
        self.currentmort = mort
