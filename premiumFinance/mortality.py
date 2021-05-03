from dataclasses import dataclass
import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot as plt
from typing import Optional

from premiumFinance.constants import DATA_FOLDER
from premiumFinance.settings import PROJECT_ROOT
from premiumFinance.fetchdata import getVBTdata

EPSILON = 1e-10


@dataclass
class Mortality:
    issueage: int
    currentage: Optional[int]
    isMale: bool
    isSmoker: Optional[bool]
    mortrate: float = 1
    whichVBT: str = "VBT01"

    def __post_init__(self):
        if self.currentage is None:
            self.currentage = self.issueage
        assert self.issueage <= self.currentage, "Issue age must not exceed current age"

    @property
    def gender(self):
        mf = "Male" if self.isMale else "Female"
        return mf

    @property
    def basemortCurv(self):
        mort = getVBTdata(
            vbt=self.whichVBT,
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            issueage=self.issueage,
            currentage=self.currentage,
        )
        return mort

    @property
    def conditional_mortality_curve(self):
        mort = self.basemortCurv
        # adjust mortality rate with multiplier
        condMort = pd.Series(min(1 - EPSILON, self.mortrate * q) for q in mort)
        return condMort

    @property
    def conditional_survival_curve(self):
        condMort = self.conditional_mortality_curve
        condSurv = 1 - condMort
        return condSurv

    @property
    def survCurv(self):
        condSurv = self.conditional_survival_curve
        surv = np.cumprod(condSurv)
        return surv

    @property
    def lifeExpectancy(self):
        surv = self.survCurv
        le = np.sum(surv)
        return le

    def plotSurvCurv(self):
        surv = self.survCurv
        le = self.lifeExpectancy
        leage = le + self.currentage
        plt.plot(surv.index + self.currentage, surv, label="Survival rate")
        plt.xlabel("Age")
        plt.ylabel("Cumulative probability")
        plt.axvline(leage, color="red", label=f"LE: {round(leage,1)}")
        plt.title(
            f"issue age: {self.issueage}, gender: {self.gender}, smoker: {self.isSmoker}"
        )
        plt.axvline(self.currentage, ls="--", lw=0.5, color="gray")
        plt.axhline(0, ls="--", lw=0.5, color="gray")
        plt.axhline(1, ls="--", lw=0.5, color="gray")
        plt.legend()
