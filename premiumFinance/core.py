from dataclasses import dataclass
import pandas as pd
import numpy as np
import constants
from os import path
import matplotlib.pyplot as plt


@dataclass
class Mortality:
    issueage: int
    currentage: int
    isMale: bool
    isSmoker: bool = None
    mortrate: float = 1

    def gender(self):
        mf = "Male" if self.isMale else "Female"
        return mf

    def basemortCurv(self, doplot=False):
        gender = self.gender()
        if self.isSmoker is None:
            filename = "unismoke"
            sheetname = f"2015 {gender} Unismoke ANB"
        else:
            filename = "smokedistinct"
            smoker = "SM" if self.isSmoker else "NS"
            gender = gender[0]
            sheetname = f"2015 {gender}{smoker} ANB"
        vbt_file = path.join(constants.DATA_FOLDER, filename + ".xlsx")
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
        condMort = pd.Series(min(1, self.mortrate * q) for q in mort)
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
        plt.plot(surv.index + self.currentage, surv)
        plt.xlabel("Age")
        plt.ylabel("Survival probability")
        plt.axvline(leage, color="orange", label=f"LE: {round(leage,1)}")
        plt.title(
            f"issue age: {self.issueage}, gender: {self.gender()}, smoker: {self.isSmoker}"
        )
        plt.axvline(self.currentage, ls="--", lw=0.5, color="gray")
        plt.axhline(0, ls="--", lw=0.5, color="gray")
        plt.legend()
