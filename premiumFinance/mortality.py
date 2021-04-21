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
    currentage: Optional[bool]
    isMale: bool
    isSmoker: Optional[bool]
    mortrate: float = 1
    whichVBT: str = "VBT01"

    def basemortCurv(self, doplot=False):
        mort = getVBTdata(
            vbt=self.whichVBT,
            isMale=self.isMale,
            isSmoker=self.isSmoker,
            issueage=self.issueage,
            currentage=self.currentage,
        )
        if doplot:
            plt.plot(mort)
        return mort

    def gender(self):
        mf = "Male" if self.isMale else "Female"
        return mf

    def basemortCurv_deprecated(self, doplot=False):
        gender = self.gender()
        if self.isSmoker is None:
            filename = "unismoke"
            sheetname = f"2015 {gender} Unismoke ANB"
        else:
            filename = "smokedistinct"
            smoker = "SM" if self.isSmoker else "NS"
            gender = gender[0]
            sheetname = f"2015 {gender}{smoker} ANB"
        vbt_file = path.join(PROJECT_ROOT, DATA_FOLDER, filename + ".xlsx")
        tbl = pd.read_excel(vbt_file, sheet_name=sheetname, header=2, index_col=0)
        maxage = max(tbl.index)
        if self.issueage <= maxage:
            curv = tbl.loc[self.issueage][:25].append(tbl["Ult."].loc[self.issueage :])
        else:
            curv = tbl.loc[maxage][(self.issueage - maxage) : 26]
        mort = pd.Series([0]).append(
            curv[(self.currentage - self.issueage) :] / 1000, ignore_index=True
        )
        if doplot:
            plt.plot(mort)
        return mort

    def condMortCurv(self, doplot=False):
        mort = self.basemortCurv()
        # adjust mortality rate with multiplier
        condMort = pd.Series(min(1 - EPSILON, self.mortrate * q) for q in mort)
        if doplot:
            plt.plot(condMort)
        return condMort

    def condSurvCurv(self, doplot=False):
        condMort = self.condMortCurv()
        condSurv = 1 - condMort
        if doplot:
            plt.plot(condSurv)
        return condSurv

    def survCurv(self):
        condSurv = self.condSurvCurv()
        surv = np.cumprod(condSurv)
        return surv

    def lifeExpectancy(self):
        surv = self.survCurv()
        le = np.sum(surv)
        return le

    def plotSurvCurv(self):
        surv = self.survCurv()
        le = self.lifeExpectancy()
        leage = le + self.currentage
        plt.plot(surv.index + self.currentage, surv, label="Survival rate")
        plt.xlabel("Age")
        plt.ylabel("Cumulative probability")
        plt.axvline(leage, color="red", label=f"LE: {round(leage,1)}")
        plt.title(
            f"issue age: {self.issueage}, gender: {self.gender()}, smoker: {self.isSmoker}"
        )
        plt.axvline(self.currentage, ls="--", lw=0.5, color="gray")
        plt.axhline(0, ls="--", lw=0.5, color="gray")
        plt.axhline(1, ls="--", lw=0.5, color="gray")
        plt.legend()
