from dataclasses import dataclass
import pandas as pd
import numpy as np
import constants
from os import path
import matplotlib.pyplot as plt
from scipy import optimize

from insured import Insured

pers_file = path.join(constants.DATA_FOLDER, "persistency.xlsx")
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

    def __post_init__(self, r_free=0, pr=0.02):
        self.r_free = r_free
        # r_free=fetchdata.getAnnualYield()
        self.pr = pr

    def lapseRate(self, doplot=False):
        if self.lapse_assumption:
            col_ind = 0 if self.insrd.isMale else 1
            lapse_rate = pd.Series([0]).append(
                tbl.iloc[:, col_ind] / 100, ignore_index=True
            )
        else:
            lapse_rate = [0]
        if doplot:
            plt.plot(lapse_rate)
        return lapse_rate

    def condPersRate(self, doplot=False):
        condSurv = self.insrd.issueMort().condSurvCurv()
        lapse_rate = self.lapseRate()

        n = len(lapse_rate)
        persrate = []
        i = 0
        for w in condSurv:
            if i < n:
                lapserate = 1 - lapse_rate[i]
                i += 1
            rate = w * lapserate
            persrate.append(rate)

        if doplot:
            plt.plot(persrate)
        return persrate

    def persRate(self):
        persrate = self.condPersRate()
        pers = np.cumprod(persrate)
        return pers

    def plotPersRate(self):
        pers = self.persRate()
        plt.plot(
            np.arange(len(pers)) + self.insrd.currentage, pers, label="Persistency rate"
        )
        self.insrd.issueMort().plotSurvCurv()

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