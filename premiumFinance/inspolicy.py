from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot as plt
from scipy import optimize
from typing import Any, List, Optional, Union


from premiumFinance.constants import DATA_FOLDER
from premiumFinance.insured import Insured
from premiumFinance.settings import PROJECT_ROOT
from premiumFinance.fetchdata import getAnnualYield


# need to `pip install openpyxl`
pers_file = path.join(PROJECT_ROOT, DATA_FOLDER, "persistency.xlsx")
# read lapse rates
lapse_tbl = pd.read_excel(
    pers_file,
    sheet_name="Universal Life",
    index_col=0,
    skiprows=8,
    skipfooter=71,
    usecols="J:K,O",
)


def extendarray(x) -> list:
    if isinstance(x, (int, float)):
        x = [x]
    if type(x) == np.ndarray:
        x = x.tolist()  # type: ignore
    if type(x) == pd.Series:
        x = x.to_list()  # type: ignore
    x.extend([x[-1]] * 150)
    return x


@dataclass
class InsurancePolicy:
    insrd: Insured
    lapse_assumption: bool = True
    prmarkup: float = 0
    surrender_penalty_rate: float = 0
    cash_interest: float = 0
    statutory_interest: Any = field(default=0.03)
    policyholder_rate: Any = field(default=0.01)  # should be some risk free rate
    pr: Any = field(default=0.002)

    def __post_init__(self):
        self.pr = extendarray(self.pr)
        self.statutory_interest = extendarray(self.statutory_interest)
        self.policyholder_rate = extendarray(self.policyholder_rate)

    # lapse rate dependent on gender; lapse == 0 with no lapse assumption
    def lapseRate(self, assumeLapse: Optional[bool] = None, doplot: bool = False):
        if assumeLapse is None:
            assumeLapse = self.lapse_assumption
        lapse_rate = pd.Series([0])
        if assumeLapse:
            col_ind = 0 if self.insrd.isMale else 1
            lapse_rate = lapse_rate.append(
                lapse_tbl.iloc[:, col_ind] / 100, ignore_index=True  # type: ignore
            )
        if doplot:
            plt.plot(lapse_rate)
        return lapse_rate

    # inforce rate starting year 1 (as opposed to year 0)
    def inforceRate(self, assumeLapse: Optional[bool] = None):
        inforcerate = (1 - self.lapseRate(assumeLapse=assumeLapse)).to_list()
        inforcerate = extendarray(inforcerate)[1:]
        return inforcerate

    def condPersRate(
        self,
        assumeLapse: Optional[bool] = None,
        atIssue: Optional[bool] = True,
        doplot: bool = False,
    ):
        inforcerate = self.inforceRate(assumeLapse=assumeLapse)
        if atIssue:
            condSurv = self.insrd.issueMort().condSurvCurv()
        else:
            condSurv = self.insrd.currentMort().condSurvCurv()
            inforcerate = inforcerate[(self.insrd.currentage - self.insrd.issueage) :]
        # print(inforcerate)

        # in year 0, inforce rate must be 100%
        inforcerate = [1] + inforcerate
        persrate = []
        i = 0
        for i, w in enumerate(condSurv):
            persrate.append(w * inforcerate[i])

        if doplot:
            plt.plot(persrate)
        return persrate

    def persRate(self, assumeLapse: Optional[bool] = None, atIssue: bool = True):
        persrate = self.condPersRate(assumeLapse=assumeLapse, atIssue=atIssue)
        pers = np.cumprod(persrate)
        return pers

    def plotPersRate(self, assumeLapse: Optional[bool] = None, atIssue: bool = True):
        pers = self.persRate(assumeLapse=assumeLapse, atIssue=atIssue)
        mort = self.insrd.issueMort() if atIssue else self.insrd.currentMort()
        ageaxis = np.arange(len(pers)) + (
            self.insrd.issueage if atIssue else self.insrd.currentage
        )
        plt.plot(ageaxis, pers, label="Persistency rate")
        mort.plotSurvCurv()

    def dbPayRate(
        self, assumeLapse: Optional[bool] = None, atIssue: bool = True, doplot=False
    ):
        pers = self.persRate(assumeLapse=assumeLapse, atIssue=atIssue)
        condmort = (
            self.insrd.issueMort().condMortCurv()
            if atIssue
            else self.insrd.currentMort().condMortCurv()
        )
        dbpayrate = pers * condmort
        if doplot:
            plt.plot(dbpayrate)
        return dbpayrate

    # `pr` is premium rate: premium / deth benefit
    def PV_pr(
        self,
        pr: Any = None,  # unpaid premium stream
        issuerPerspective: Optional[bool] = True,
        assumeLapse: Optional[bool] = True,
        atIssue: bool = True,
        discount_rate: Optional[Union[float, List[float]]] = None,
    ) -> float:

        pers = self.persRate(assumeLapse=assumeLapse, atIssue=atIssue)
        if issuerPerspective is not None:
            discount_rate = (
                self.statutory_interest if issuerPerspective else self.policyholder_rate
            )

        if pr is None:
            starting_period = (
                0 if atIssue else (self.insrd.currentage - self.insrd.issueage)
            )

            pr = self.pr[starting_period:]
        else:
            pr = extendarray(pr)

        obs_period = len(pers)

        cf = 0
        for i in range(obs_period):
            cf += (pers[i] * pr[i]) / (1 + discount_rate[i]) ** i  # type: ignore

        return cf

    def PV_db(
        self,
        issuerPerspective: Optional[bool] = True,
        assumeLapse: Optional[bool] = None,
        atIssue: bool = True,
        discount_rate: Any = None,
    ) -> float:

        if issuerPerspective is not None:
            discount_rate = (
                self.statutory_interest if issuerPerspective else self.policyholder_rate
            )

        cf = 0
        oneperiod_mort = self.dbPayRate(
            assumeLapse=assumeLapse,
            atIssue=atIssue,
        )
        for i, m in enumerate(oneperiod_mort):
            cf += m / (1 + discount_rate[i]) ** i
        return cf

    def policyvalue(
        self,
        pr=None,
        issuerPerspective: Optional[bool] = True,
        assumeLapse: Optional[bool] = None,
        atIssue: bool = True,
        discount_rate: Optional[float] = None,
    ):

        PVdb = self.PV_db(
            issuerPerspective=issuerPerspective,
            assumeLapse=assumeLapse,
            atIssue=atIssue,
            discount_rate=discount_rate,
        )
        PVpr = self.PV_pr(
            pr=pr,
            issuerPerspective=issuerPerspective,
            assumeLapse=assumeLapse,
            atIssue=atIssue,
            discount_rate=discount_rate,
        )
        pft = PVdb - PVpr
        return pft

    def getLevelpr(
        self, assumeLapse: bool = None, newPolicy: bool = False, addMarkup: bool = True
    ) -> float:
        sol = optimize.root_scalar(
            lambda pr: self.policyvalue(
                pr,
                issuerPerspective=True,
                assumeLapse=assumeLapse,
                atIssue=not newPolicy,
            ),
            x0=0.004,
            bracket=[0, 1],
            method="brentq",
        )
        levelpr = sol.root * (1 + (self.prmarkup if addMarkup else 0))
        return levelpr

    def getIRR(
        self,
        pr=None,
        levelPr: bool = None,
        lapse_based_pricing: bool = None,
        assumeLapse: bool = None,
        atIssue: bool = True,
    ):
        if pr is None:
            if levelPr is None:
                pr = self.pr
            else:
                pr = (
                    self.getLevelpr(assumeLapse=lapse_based_pricing)
                    if levelPr
                    else self.getVariablePr(assumeLapse=lapse_based_pricing)
                )
            starting_period = (
                0 if atIssue else (self.insrd.currentage - self.insrd.issueage)
            )
            pr = self.pr[starting_period:]
        pr = extendarray(pr)

        sol = optimize.root_scalar(
            lambda r: self.policyvalue(
                pr=pr,
                issuerPerspective=None,
                assumeLapse=assumeLapse,
                atIssue=atIssue,
                discount_rate=r,
            ),
            x0=0.0001,
            bracket=[0, 0.99],
            method="brentq",
        )
        return sol.root

    def getVariablePr(
        self, assumeLapse: bool = None, addMarkup: bool = True, doplot=False
    ):
        pr = self.insrd.issueMort().condMortCurv() / self.condPersRate(
            assumeLapse=assumeLapse
        )

        pr = pr * (1 + (self.prmarkup if addMarkup else 0))
        if doplot:
            plt.plot(pr)
            plt.ylim(0, 1)
        return pr
