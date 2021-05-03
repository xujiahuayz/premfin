from dataclasses import dataclass
from scipy import optimize
import numpy as np
from premiumFinance.inspolicy import InsurancePolicy, extendarray
from typing import Any, Optional, Type, Union, List


@dataclass
class PolicyFinancingScheme:
    policy: InsurancePolicy

    def PV_unpaid_premium_policyholder(
        self,
    ):
        return self.policy.PV_unpaid_premium(
            premium_stream_at_issue=self.policy.premium_stream_at_issue,
            issuer_perspective=False,
            at_issue=False,
        )

    def PV_death_benefit_policyholder(self) -> float:
        return self.policy.PV_death_benefit(issuer_perspective=False, at_issue=False)

    def unpaid_pr(self):
        starting_period = (
            self.policy.insured.current_age - self.policy.insured.issue_age
        )
        pr = self.policy.premium_stream_at_issue[starting_period:]
        return pr

    def PV_repay(
        self,
        loanrate: float,
        oneperiod_mort: Any = None,
    ) -> float:
        pr = self.unpaid_pr()

        if oneperiod_mort is None:
            oneperiod_mort = self.policy.death_benefit_payment_rate(
                assume_lapse=False, at_issue=False
            )

        discount_rate = self.policy.policyholder_rate

        cf = 0.0

        for i in range(len(oneperiod_mort) - 1):
            debt = 0
            for j in range(i):
                debt += pr[j] * (1 + loanrate) ** (i + 1 - j)
            debt *= oneperiod_mort[i + 1]

            cf += debt / (1 + discount_rate[i + 1]) ** (i + 1)

        return cf

    def PV_borrower(
        self,
        loanrate: float,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
        oneperiod_mort: Any = None,
    ) -> float:
        if pv_deathben is None:
            pv_deathben = self.PV_death_benefit_policyholder()
        pv = pv_deathben - self.PV_repay(
            loanrate=loanrate, oneperiod_mort=oneperiod_mort
        )
        if not fullrecourse:
            pv = max(0, pv)
        return pv

    def PV_lender(
        self,
        loanrate: float,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
    ) -> float:
        in_flow = self.PV_repay(loanrate=loanrate)
        if not fullrecourse:
            if pv_deathben is None:
                pv_deathben = self.PV_death_benefit_policyholder()
            in_flow = min(pv_deathben, in_flow)
        pv = in_flow - self.PV_unpaid_premium_policyholder()
        return pv

    def PV_lender_maxed(
        self,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
    ) -> float:
        loanrate = self.breakevenLoanRate(fullrecourse=fullrecourse)
        pv = self.PV_lender(
            loanrate=loanrate,
            fullrecourse=fullrecourse,
            pv_deathben=pv_deathben,
        )
        return pv

    def surrender_value(self) -> float:

        variablepr = self.policy._variable_premium
        pr = self.policy.premium_stream_at_issue
        sv = 0
        obs_period = self.policy.insured.current_age - self.policy.insured.issue_age

        for i, vp in enumerate(variablepr[:obs_period]):
            sv += (pr[i] - vp) / (1 + self.policy.cash_interest) ** i
        sv *= 1 - self.policy.surrender_penalty_rate
        return max(sv, 0)  # surrender value cannot be negative

    def breakevenLoanRate(
        self,
        fullrecourse: bool = True,
    ) -> float:
        sv = self.surrender_value()
        oneperiod_mort = self.policy.death_benefit_payment_rate(
            assume_lapse=False, at_issue=False
        )
        pv_deathben = self.PV_death_benefit_policyholder()
        sol = optimize.root_scalar(
            lambda r: self.PV_borrower(
                loanrate=r,
                fullrecourse=fullrecourse,
                pv_deathben=pv_deathben,
                oneperiod_mort=oneperiod_mort,
            )
            - sv,
            x0=0.001,
            bracket=[-0.5, 3],
            method="brentq",
        )
        return sol.root