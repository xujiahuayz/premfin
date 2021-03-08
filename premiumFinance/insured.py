from dataclasses import dataclass
import pandas as pd
import numpy as np
import constants
from os import path

from core import Mortality


@dataclass
class Insured:
    issueage: int
    currentage: int
    isMale: bool
    isSmoker: bool = None
    mortrate: float = 1

    def __post_init__(self):
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

    def indiMort(self):
        im = Mortality(
            issueage=self.issueage,
            currentage=self.currentage,
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            mortrate=self.mortrate,
        )
        return im
