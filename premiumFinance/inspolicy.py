from dataclasses import dataclass
import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot as plt
from scipy import optimize
from typing import Any


from premiumFinance.constants import DATA_FOLDER
from premiumFinance.insured import Insured
from premiumFinance.settings import PROJECT_ROOT
from premiumFinance.fetchdata import getAnnualYield

# need to `pip install openpyxl`

pers_file = path.join(PROJECT_ROOT, DATA_FOLDER, "persistency.xlsx")
tbl = pd.read_excel(
    pers_file,
    sheet_name="Universal Life",
    index_col=0,
    skiprows=8,
    skipfooter=71,
    usecols="J:K,O",
)


@dataclass
class InsurancePolicy:
    insrd: Insured
    lapse_assumption: bool = True
    spread: float = 0
    r_free: Any = 0.01
    pr: Any = 0.02

    # lapse rate dependent on gender; lapse == 0 with no lapse assumption
    def lapseRate(self, doplot=False):
        lapse_rate = pd.Series([0])
        if self.lapse_assumption:
            col_ind = 0 if self.insrd.isMale else 1
            lapse_rate = lapse_rate.append(
                tbl.iloc[:, col_ind] / 100, ignore_index=True
            )
        if doplot:
            plt.plot(lapse_rate)
        return lapse_rate

    def inforceRate(self):
        inforcerate = (1 - self.lapseRate()).to_list()
        inforcerate.extend([inforcerate[-1]] * 200)
        return inforcerate[1:]

    def condPersRate(self, doplot: bool = False, atIssue: bool = True):
        inforcerate = self.inforceRate()
        if atIssue:
            condSurv = self.insrd.issueMort().condSurvCurv()
        else:
            condSurv = self.insrd.currentMort().condSurvCurv()
            inforcerate = inforcerate[(self.insrd.currentage - self.insrd.issueage) :]
        print(inforcerate)
        inforcerate = [1] + inforcerate
        persrate = []
        i = 0
        for i, w in enumerate(condSurv):
            persrate.append(w * inforcerate[i])

        if doplot:
            plt.plot(persrate)
        return persrate

    def persRate(self, atIssue: bool = True):
        persrate = self.condPersRate(atIssue=atIssue)
        pers = np.cumprod(persrate)
        return pers

    def plotPersRate(self, atIssue: bool = True):
        pers = self.persRate(atIssue=atIssue)
        mort = self.insrd.issueMort() if atIssue else self.insrd.currentMort()
        ageaxis = np.arange(len(pers)) + (
            self.insrd.issueage if atIssue else self.insrd.currentage
        )
        plt.plot(ageaxis, pers, label="Persistency rate")
        mort.plotSurvCurv()

    def dbPayRate(self, doplot=False):
        pers = self.persRate()
        condmort = self.insrd.issueMort().condMortCurv()
        dbpayrate = pers * condmort
        if doplot:
            plt.plot(dbpayrate)
        return dbpayrate

    # `pr` is premium rate: premium / deth benefit
    def getPV_pr(self, pr=None, r_free=None) -> float:

        surv = self.persRate()

        if r_free is None:
            r_free = self.r_free

        if pr is None:
            pr = self.pr

        if isinstance(r_free, (int, float)):
            r_free = [r_free] * len(surv)

        cf = 0
        if isinstance(pr, (int, float)):
            # assert pr < 1, 'premium rate must be below 1'
            for i in range(len(surv)):
                cf += surv[i] / (1 + r_free[i]) ** i
            cf *= pr

        else:
            assert len(surv) == len(
                pr
            ), "survial curve and premium curve must have the same length"
            # assert all(p < 1 for p in pr), 'premium rates must be all below 1'
            for i in range(len(surv)):
                cf += (surv[i] * pr[i]) / (1 + r_free[i]) ** i

        return cf

    def getPV_db(self, r_free=None) -> float:

        surv = self.persRate()
        if r_free is None:
            r_free = self.r_free
        if isinstance(r_free, (int, float)):
            r_free = [r_free] * len(surv)

        cf = 0
        oneperiod_mort = self.dbPayRate()
        for i in oneperiod_mort.index:
            cf += oneperiod_mort[i] / (1 + r_free[i]) ** i
        return cf

    def insurerProfit(self, pr=None, r_free=None):
        PVdb = self.getPV_db(r_free)
        PVpr = self.getPV_pr(pr=pr, r_free=r_free)
        pft = PVpr - PVdb
        return pft

    def getFlatpr(self):
        sol = optimize.root_scalar(
            lambda pr: self.insurerProfit(pr),
            x0=0.004,
            bracket=[0, 1],
            method="brentq",
        )
        return sol.root

    def getIRR(self):
        breakEvenFlatpr = self.getFlatpr()
        sol = optimize.root_scalar(
            lambda r: self.insurerProfit(
                pr=breakEvenFlatpr,
                r_free=r,
            ),
            x0=0.0001,
            bracket=[0, 0.99],
            method="brentq",
        )
        return sol.root

    def breakEvenPremium(self, doplot=False):
        pr = self.insrd.issueMort().condMortCurv() / self.condPersRate()
        if doplot:
            plt.plot(pr)
            plt.ylim(0, 1)
        return pr

    def updatePr(self, pr):
        self.pr = pr

    def updateRfree(self, r_free):
        self.r_free = r_free

    # def variablePremium(self):
    #     pr = self.breakEvenPremium()
    #     vp = pr + self.spread
    #     return vp