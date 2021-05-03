from dataclasses import dataclass, field
from numpy.core.arrayprint import BoolFormat
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
pers_file = path.join(DATA_FOLDER, "persistency.xlsx")
# read lapse rates
lapse_tbl = pd.read_excel(
    pers_file,
    sheet_name="Universal Life",
    index_col=0,
    skiprows=8,
    skipfooter=71,
    usecols="J:K,O",
)


def extendarray(x, to_length: int = 150) -> list:
    if isinstance(x, (int, float)):
        x = [x]
    if type(x) == np.ndarray:
        x = x.tolist()  # type: ignore
    if type(x) == pd.Series:
        x = x.to_list()  # type: ignore
    x_lenghth = len(x)
    if x_lenghth < to_length:
        x.extend([x[-1]] * (to_length - x_lenghth))
    return x


@dataclass
class InsurancePolicy:
    insured: Insured
    lapse_assumption: bool = True
    premium_markup: float = 0
    surrender_penalty_rate: float = 0
    cash_interest: float = 0
    is_level_premium: Optional[bool] = None
    premium_stream_at_issue: Union[float, List[float], None] = None
    statutory_interest: Union[float, List[float]] = 0.03
    policyholder_rate: Union[float, List[float]] = 0.01  # should be some risk free rate

    def __post_init__(self):
        assert (
            (self.is_level_premium == None) + (self.premium_stream_at_issue == None)
        ) == 1, "one and only one of `is_level_premium` and `premium_stream_at_issue` can be None"

        self.statutory_interest = extendarray(self.statutory_interest)
        self.policyholder_rate = extendarray(self.policyholder_rate)

        if self.is_level_premium:
            premium_stream_at_issue = self._level_premium
        elif self.is_level_premium == False:
            premium_stream_at_issue = self._variable_premium
        self.premium_stream_at_issue = extendarray(premium_stream_at_issue)

    # lapse rate dependent on gender; lapse == 0 with no lapse assumption
    def lapse_rate(self, assume_lapse: bool):
        lapse_rate = pd.Series([0])
        if assume_lapse:
            col_ind = 0 if self.insured.isMale else 1
            lapse_rate = lapse_rate.append(
                lapse_tbl.iloc[:, col_ind] / 100, ignore_index=True  # type: ignore
            )
        return lapse_rate

    # inforce rate starting year 1 (as opposed to year 0)
    def inforce_rate(self, assume_lapse: bool):
        inforcerate = (1 - self.lapse_rate(assume_lapse=assume_lapse)).to_list()
        inforcerate = extendarray(inforcerate)[1:]
        return inforcerate

    def conditional_persistency_curve(
        self,
        assume_lapse: bool,
        at_issue: bool = True,
    ):
        inforcerate = self.inforce_rate(assume_lapse=assume_lapse)
        if at_issue:
            condSurv = self.insured.mortality_at_issue.conditional_survival_curve
        else:
            condSurv = self.insured.currentMort.conditional_survival_curve
            inforcerate = inforcerate[
                (self.insured.current_age - self.insured.issue_age) :
            ]

        # in year 0, inforce rate must be 100%
        inforcerate = [1] + inforcerate
        persistency_rate = []
        i = 0
        for i, w in enumerate(condSurv):
            persistency_rate.append(w * inforcerate[i])
        return persistency_rate

    def persistency_rate(self, assume_lapse: bool, at_issue: bool = True):
        persrate = self.conditional_persistency_curve(
            assume_lapse=assume_lapse, at_issue=at_issue
        )
        pers = np.cumprod(persrate)
        return pers

    def plotPersRate(self, assume_lapse: bool, atIssue: bool = True):
        pers = self.persistency_rate(assume_lapse=assume_lapse, at_issue=atIssue)
        mort = self.insured.mortality_at_issue if atIssue else self.insured.currentMort
        ageaxis = np.arange(len(pers)) + (
            self.insured.issue_age if atIssue else self.insured.current_age
        )
        plt.plot(ageaxis, pers, label="Persistency rate")
        mort.plotSurvCurv()

    def death_benefit_payment_rate(self, assume_lapse: bool, at_issue: bool = True):
        pers = self.persistency_rate(assume_lapse=assume_lapse, at_issue=at_issue)
        condmort = (
            self.insured.mortality_at_issue.conditional_mortality_curve
            if at_issue
            else self.insured.currentMort.conditional_mortality_curve
        )
        dbpayrate = pers * condmort
        return dbpayrate

    # `pr` is premium rate: premium / deth benefit
    def PV_unpaid_premium(
        self,
        issuer_perspective: bool,
        at_issue: bool = True,
        premium_stream_at_issue: Union[float, List[float], None] = None,
        discount_rate: Union[float, List[float], None] = None,
    ) -> float:

        pers = self.persistency_rate(
            assume_lapse=self.lapse_assumption if issuer_perspective else True,
            at_issue=at_issue,
        )
        if discount_rate is None:
            discount_rate = (
                self.statutory_interest
                if issuer_perspective
                else self.policyholder_rate
            )
        discount_rate = extendarray(discount_rate)

        if premium_stream_at_issue is None:
            premium_stream_at_issue = self.premium_stream_at_issue

        premium_stream_at_issue = extendarray(premium_stream_at_issue)

        starting_period = (
            0 if at_issue else (self.insured.current_age - self.insured.issue_age)
        )

        unpaid_premium = premium_stream_at_issue[starting_period:]

        obs_period = len(pers)

        cf = 0
        for i in range(obs_period):
            cf += (pers[i] * unpaid_premium[i]) / (1 + discount_rate[i]) ** i  # type: ignore

        return cf

    def PV_death_benefit(
        self,
        issuer_perspective: bool,
        at_issue: bool = True,
        discount_rate: Union[float, List[float], None] = None,
    ) -> float:

        if discount_rate is None:
            discount_rate = (
                self.statutory_interest
                if issuer_perspective
                else self.policyholder_rate
            )
        discount_rate = extendarray(discount_rate)

        cf = 0
        one_period_mortality = self.death_benefit_payment_rate(
            assume_lapse=self.lapse_assumption
            if issuer_perspective
            else False,  # insureds do not assume lapse
            at_issue=at_issue,
        )
        for i, m in enumerate(one_period_mortality):
            cf += m / (1 + discount_rate[i]) ** i
        return cf

    def policy_value(
        self,
        premium_stream_at_issue: Union[float, List[float], None] = None,
        issuer_perspective: bool = True,
        at_issue: bool = True,
        discount_rate: Union[float, List[float], None] = None,
    ):

        if discount_rate is None:
            discount_rate = (
                self.statutory_interest
                if issuer_perspective
                else self.policyholder_rate
            )

        discount_rate = extendarray(discount_rate)

        if premium_stream_at_issue is None:
            premium_stream_at_issue = self.premium_stream_at_issue
        else:
            premium_stream_at_issue = extendarray(premium_stream_at_issue)

        PVdb = self.PV_death_benefit(
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        )
        PVpr = self.PV_unpaid_premium(
            premium_stream_at_issue=premium_stream_at_issue,
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        )
        surplus = PVpr - PVdb
        return surplus
        # if issuer_perspective else -surplus

    @property
    def _level_premium(self, newPolicy: bool = False) -> float:
        sol = optimize.root_scalar(
            lambda p: self.policy_value(
                premium_stream_at_issue=p,
                issuer_perspective=True,
                at_issue=not newPolicy,
            ),
            x0=0.004,
            bracket=[0, 1],
            method="brentq",
        )
        levelpr = sol.root * (1 + self.premium_markup)
        return levelpr

    def getIRR(
        self,
        issuer_perspecitve: bool = True,
        at_issue: bool = True,
    ):

        sol = optimize.root_scalar(
            lambda r: self.policy_value(
                premium_stream_at_issue=self.premium_stream_at_issue,
                issuer_perspective=issuer_perspecitve,
                at_issue=at_issue,
                discount_rate=r,
            ),
            x0=0.0001,
            bracket=[0, 0.99],
            method="brentq",
        )
        return sol.root

    @property
    def _variable_premium(self):
        pr = (
            self.insured.mortality_at_issue.conditional_mortality_curve
            / self.conditional_persistency_curve(assume_lapse=self.lapse_assumption)
        )

        pr = pr * (1 + self.premium_markup)
        return pr
