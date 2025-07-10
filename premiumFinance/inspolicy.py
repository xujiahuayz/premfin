"""
Insurance policy class and its methods
"""

from dataclasses import dataclass
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

from premiumFinance.insured import Insured
from premiumFinance.util import cash_flow_pv, lapse_rate, make_list


@dataclass
class InsurancePolicy:
    """
    insurance policy class
    """

    insured: Insured
    lapse_assumption: bool = True
    premium_markup: float = 0
    surrender_penalty_rate: float = 0.3
    cash_interest: float = 0.002
    is_level_premium: bool | None = None
    premium_stream_at_issue: float | Iterable[float] | None = None
    statutory_interest: float | Iterable[float] = 0.05
    policyholder_rate: float | Iterable[float] = 0.01  # should be some risk free rate

    def __post_init__(self):
        assert (
            (self.is_level_premium == None) + (self.premium_stream_at_issue == None)
        ) == 1, "one and only one of `is_level_premium` and `premium_stream_at_issue` can be None"

        # if self.premium_stream_at_issue is not None:
        self.statutory_interest = make_list(self.statutory_interest)
        self.policyholder_rate = make_list(self.policyholder_rate)

        if self.is_level_premium:
            premium_stream_at_issue = self._level_premium
        elif self.is_level_premium == False:
            premium_stream_at_issue = self._variable_premium
        self.premium_stream_at_issue = make_list(premium_stream_at_issue)

    # inforce rate starting year 1 (as opposed to year 0)
    def in_force_rate(self, assume_lapse: bool) -> list[float]:
        """
        policy in-force rate based on lapse assumption and gender
        """

        inforcerate = [
            1 - x for x in lapse_rate(self.insured.is_male, assume_lapse=assume_lapse)
        ]
        return make_list(inforcerate)

    def conditional_persistency_curve(
        self,
        assume_lapse: bool,
        at_issue: bool = True,
    ) -> list[float]:
        """
        conditional persistency curve of the policyholder
        """

        inforcerate = self.in_force_rate(assume_lapse=assume_lapse)
        if at_issue:
            condSurv = self.insured.mortality_at_issue.conditional_survival_curve
        else:
            condSurv = self.insured.mortality_now.conditional_survival_curve
            inforcerate = inforcerate[
                (self.insured.current_age - self.insured.issue_age+1) :
            ]
            # in year 0, inforce rate must be 100%
            inforcerate = [1] + inforcerate

        
        persistency_rate = []
        i = 0
        for i, w in enumerate(condSurv):
            # if out of bound, just use the previous ir
            try:
                ir = inforcerate[i]
            except IndexError:
                pass
            persistency_rate.append(w * ir)
        return persistency_rate

    def persistency_rate(self, assume_lapse: bool, at_issue: bool = True) -> np.ndarray:
        """
        unconditional persistency rates (should converge to zero as time goes)
        """

        persrate = self.conditional_persistency_curve(
            assume_lapse=assume_lapse, at_issue=at_issue
        )
        pers = np.cumprod(persrate)
        return pers

    def plot_pers_rate(self, assume_lapse: bool, atIssue: bool = True) -> None:
        """
        plot persistency rates
        """

        pers = self.persistency_rate(assume_lapse=assume_lapse, at_issue=atIssue)
        mort = (
            self.insured.mortality_at_issue if atIssue else self.insured.mortality_now
        )
        ageaxis = np.arange(len(pers)) + (
            self.insured.issue_age if atIssue else self.insured.current_age
        )
        plt.plot(ageaxis, pers, label="Persistency rate")
        mort.plot_surv_curv()

    def death_benefit_payment_probability(
        self, assume_lapse: bool, at_issue: bool = True
    ) -> list[float]:
        """
        probabilities of death benefit payment
        """

        persistency = self.persistency_rate(
            assume_lapse=assume_lapse, at_issue=at_issue
        )
        one_period_conditional_mortality = (
            self.insured.mortality_at_issue.conditional_mortality_curve
            if at_issue
            else self.insured.mortality_now.conditional_mortality_curve
        )
        return [
            a * b
            for a, b in zip(
                [1] + persistency.tolist(), one_period_conditional_mortality.to_list()
            )
        ]
    

    def cash_surrender_probability(
        self, assume_lapse: bool, at_issue: bool = True
    ) -> list[float]:
        """
        probabilities of death benefit payment
        """

        persistency = self.persistency_rate(
            assume_lapse=assume_lapse, at_issue=at_issue
        )
        one_period_conditional_mortality = (
            self.insured.mortality_at_issue.conditional_mortality_curve
            if at_issue
            else self.insured.mortality_now.conditional_mortality_curve
        )

        inforcerate = self.in_force_rate(assume_lapse=assume_lapse)
        if not at_issue:
            inforcerate = inforcerate[
                (self.insured.current_age - self.insured.issue_age) :
            ]
             # in year 0, inforce rate must be 100%
            inforcerate = [1] + inforcerate

        return [
            a * (1-b) * (1-c)
            for a, b, c in zip(
                [1] + persistency.tolist(), one_period_conditional_mortality.to_list(), inforcerate
            )
        ]

    # `pr` is premium rate: premium / death benefit
    def pv_unpaid_premium_list(
        self,
        at_issue: bool = False,
        issuer_perspective: bool | None = None,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        discount_rate: float | Iterable[float] | None = None,
    ) -> list[float]:
        """
        unpaid premium stream discounted to present value
        """

        # investor or issuer does not assume lapse
        pers = self.persistency_rate(
            assume_lapse=self.lapse_assumption if issuer_perspective else False,
            at_issue=at_issue,
        )
        if discount_rate is None:
            assert (
                issuer_perspective is not None
            ), "discount_rate and issuer_perspective cannot be simultaneously None"
            discount_rate = (
                self.statutory_interest
                if issuer_perspective
                else self.policyholder_rate
            )
        discount_rate = make_list(discount_rate)

        if premium_stream_at_issue is None:
            premium_stream_at_issue = self.premium_stream_at_issue

        premium_stream_at_issue = make_list(premium_stream_at_issue)

        starting_period = (
            0 if at_issue else (self.insured.current_age - self.insured.issue_age)
        )
        unpaid_premium = premium_stream_at_issue[starting_period:]

        # print(f"Pr discount {discount_rate}")

        return cash_flow_pv(
            cashflow=unpaid_premium, probabilities=pers, discounters=discount_rate
        )

    def pv_unpaid_premium(
        self,
        at_issue: bool = False,
        issuer_perspective: bool | None = None,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        discount_rate: float | Iterable[float] | None = None,
    ) -> float:
        """
        present value of all unpaid, probabilistic premium
        """

        return sum(
            self.pv_unpaid_premium_list(
            at_issue=at_issue,
            issuer_perspective=issuer_perspective,
            premium_stream_at_issue=premium_stream_at_issue,
            discount_rate=discount_rate,
        ))

    def pv_death_benefit_list(
        self,
        issuer_perspective: bool | None = None,
        at_issue: bool = True,
        discount_rate: float | Iterable[float] | None = None,
    ) -> list[float]:
        """
        probabilistic death benefit payments discount to present value
        """

        if discount_rate is None:
            assert (
                issuer_perspective is not None
            ), "discount_rate and issuer_perspective cannot be simultaneously None"
            discount_rate = (
                self.statutory_interest
                if issuer_perspective
                else self.policyholder_rate
            )

        one_period_mortality = self.death_benefit_payment_probability(
            assume_lapse=(
                self.lapse_assumption if issuer_perspective else False
            ),  # insureds / lenders do not assume lapse
            at_issue=at_issue,
        )

        return cash_flow_pv(
            cashflow=1, probabilities=one_period_mortality, discounters=discount_rate
        )

    def pv_death_benefit(
        self,
        issuer_perspective: bool | None = None,
        at_issue: bool = True,
        discount_rate: float | Iterable[float] | None = None,
    ) -> float:
        """
        present value of death benefit payment
        """

        return sum(
            self.pv_death_benefit_list(
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        ))
    
    def cash_value_list(
        self,
        premium_stream_at_issue: float | Iterable[float] | None = None
    ) -> list[float]:
        """
        probabilistic present values of future values (one value per period) of the policy
        """

        if premium_stream_at_issue is None:
            premium_stream_at_issue = self.premium_stream_at_issue

        premium_stream_at_issue = make_list(premium_stream_at_issue)

        variablepr = self._variable_premium
        # obs_period = self.insured.current_age - self.insured.issue_age
        cash_interest = self.cash_interest

        surrender_value_list = []
        surrender_value = 0
        for i, vpr in enumerate(variablepr):
            surrender_value = max((
                premium_stream_at_issue[i] - vpr + surrender_value * (1 + cash_interest)
            ),0) 
            surrender_value_list.append(surrender_value * (1 - self.surrender_penalty_rate))

        return surrender_value_list
    
    def pv_csv_list(
        self,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        issuer_perspective: bool | None = None,
        at_issue: bool = True,
        discount_rate: float | Iterable[float] | None = None,
    ) -> list[float]:
        """
        present value of death benefit payment
        """

        if discount_rate is None:
            assert (
                issuer_perspective is not None
            ), "discount_rate and issuer_perspective cannot be simultaneously None"
            discount_rate = (
                self.statutory_interest
                if issuer_perspective
                else self.policyholder_rate
            )


        return cash_flow_pv(
            cashflow=self.cash_value_list(premium_stream_at_issue=premium_stream_at_issue), 
            probabilities=self.cash_surrender_probability(
            assume_lapse=(
                self.lapse_assumption if issuer_perspective else False
            ),  # insureds / lenders do not assume lapse
            at_issue=at_issue,
        ), 
            discounters=discount_rate
        )
    

    def pv_csv(
        self,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        issuer_perspective: bool | None = None,
        at_issue: bool = True,
        discount_rate: float | Iterable[float] | None = None,
    ) -> float:
        """
        present value of death benefit payment
        """

        return sum(self.pv_csv_list(
            premium_stream_at_issue=premium_stream_at_issue,
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        ))
            

    def policy_value_list(
        self,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        issuer_perspective: bool | None = None,
        at_issue: bool = True,
        discount_rate: float | Iterable[float] | None = None,
    ) -> list[float]:
        """
        present value of probabilistic cash flow (premium - death benefit - cash surrender value)
        """

        if premium_stream_at_issue is None:
            premium_stream_at_issue = self.premium_stream_at_issue
        else:
            premium_stream_at_issue = make_list(premium_stream_at_issue)

        pv_db = self.pv_death_benefit_list(
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        )
        pv_pr = self.pv_unpaid_premium_list(
            premium_stream_at_issue=premium_stream_at_issue,
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        )

        pv_sv = self.pv_csv_list(
            premium_stream_at_issue=premium_stream_at_issue,
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        )

        return [p - d - s  for d, p, s in zip(pv_db, pv_pr, pv_sv)]

    def policy_value(
        self,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        issuer_perspective: bool | None = None,
        at_issue: bool = True,
        discount_rate: float | Iterable[float] | None = None,
    ) -> float:
        """
        present value of a policy
        """

        return sum(self.policy_value_list(
            premium_stream_at_issue=premium_stream_at_issue,
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        ))

    def policy_value_future_list(
        self,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        issuer_perspective: bool | None = None,
        at_issue: bool = True,
        discount_rate: float | Iterable[float] | None = None,
    ) -> list[float]:
        """
        probabilistic present values of future values (one value per period) of the policy
        """

        cash_stream = self.policy_value_list(
            premium_stream_at_issue=premium_stream_at_issue,
            issuer_perspective=issuer_perspective,
            at_issue=at_issue,
            discount_rate=discount_rate,
        )
        probabilistic_PV_of_FV = []
        for i, _ in enumerate(cash_stream):
            probabilistic_PV_of_FV.append(sum(cash_stream[i:]))

        return probabilistic_PV_of_FV

    

    def nav_gain(
        self,
        at_issue: bool = False,
        premium_stream_at_issue: float | Iterable[float] | None = None,
        discount_rate: float | Iterable[float] | None = None,
    ) -> list[float]:
        """
        year-by-year gain in policy nav
        """

        discount_rate = self.policyholder_rate
        discount_rate = make_list(discount_rate)

        probabilistic_PV_of_FV = self.policy_value_future_list(
            premium_stream_at_issue=premium_stream_at_issue,
            issuer_perspective=False,
            at_issue=at_issue,
            discount_rate=discount_rate,
        )

        unconditional_pers = self.persistency_rate(
            assume_lapse=False,
            at_issue=at_issue,
        )

        sum_until = min(
            len(probabilistic_PV_of_FV), len(discount_rate), len(unconditional_pers)
        )

        fv_nav = [
            -c * (1 + discount_rate[i]) ** i / unconditional_pers[i]
            for i, c in enumerate(probabilistic_PV_of_FV[:sum_until])
        ]

        nav_increase = np.diff(fv_nav).tolist()
        nav_increase_from_now = [0] + nav_increase

        return cash_flow_pv(
            cashflow=nav_increase_from_now,
            probabilities=unconditional_pers,
            discounters=discount_rate,
        )

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
    def _variable_premium(self) -> list[float]:
        # variable premium shouldn't exceed 1 death benefit per year
        return [
            min(a / b * (1 + self.premium_markup), 1)
            for a, b in zip(
                self.death_benefit_payment_probability(
                    assume_lapse=self.lapse_assumption, at_issue=True
                ),
                self.persistency_rate(
                    assume_lapse=self.lapse_assumption, at_issue=True
                ),
            )
        ]


if __name__ == "__main__":

    Alice = Insured(
        issue_age=60,
        current_age=75,
        is_male=True,
        issue_vbt="VBT01",
    )
    Alice_policy = InsurancePolicy(Alice, is_level_premium=True, lapse_assumption=True)

    Alice_policy.persistency_rate(assume_lapse=True, at_issue=True)
    Alice_policy.cash_surrender_probability(
        assume_lapse=True, at_issue=True
    )
    Alice_policy.death_benefit_payment_probability(
        assume_lapse=True, at_issue=True)
    
    Alice_policy._level_premium
    Alice_policy._variable_premium

    Alice_policy2 = InsurancePolicy(
        Alice, is_level_premium=True, lapse_assumption=False
    )
    Alice_policy2._level_premium
