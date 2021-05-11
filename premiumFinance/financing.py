from dataclasses import dataclass

from pandas.io.parsers import ParserBase
from premiumFinance.util import cash_flow_pv
from scipy import optimize
import numpy as np
from premiumFinance.inspolicy import InsurancePolicy, make_list
from typing import Any, Optional, Type, Union, List


@dataclass
class PolicyFinancingScheme:
    policy: InsurancePolicy
    lender_coc: float = 0.01

    # def PV_death_benefit_policyholder(self) -> float:
    #     return self.policy.PV_death_benefit(issuer_perspective=False, at_issue=False)

    def unpaid_pr(self):
        starting_period = (
            self.policy.insured.current_age - self.policy.insured.issue_age
        )
        pr = self.policy.premium_stream_at_issue[starting_period:]
        return pr

    def PV_repay(
        self,
        loanrate: float,
        discount_rate: Any,
        oneperiod_mort: Any = None,
    ) -> float:
        pr = make_list(self.unpaid_pr())

        # Note: every repay element corresponds to mortality rate,
        # i.e. the repay amount when you DIE at the beginning of a period (given survival last period)
        # therefore, DO NOT include this period's premium!
        cumulative_loan = 0.0
        loan_cash_flow = [cumulative_loan]
        for i in range(len(pr))[1:]:
            cumulative_loan = (cumulative_loan + pr[i - 1]) * (1 + loanrate)
            loan_cash_flow.append(cumulative_loan)

        if oneperiod_mort is None:
            # investor / policyholder usually does not assume lapse
            oneperiod_mort = self.policy.death_benefit_payment_probability(
                assume_lapse=False, at_issue=False
            )

        # this is to make sure that unconditional mortality rate in the end converges to 0!!
        oneperiod_mort = oneperiod_mort + [0.0] * 250

        return cash_flow_pv(
            cashflow=loan_cash_flow,
            probabilities=oneperiod_mort,
            discounters=discount_rate,
        )

        # # discount_rate = self.policy.policyholder_rate

        # cf = 0.0

        # for i in range(len(oneperiod_mort) - 1):
        #     debt = 0
        #     for j in range(i):
        #         debt += pr[j] * (1 + loanrate) ** (i + 1 - j)
        #     debt *= oneperiod_mort[i + 1]

        #     cf += debt / (1 + discount_rate[i + 1]) ** (i + 1)

        # return cf

    def PV_borrower(
        self,
        loanrate: float,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
        oneperiod_mort: Any = None,
    ) -> float:
        if pv_deathben is None:
            pv_deathben = self.policy.PV_death_benefit(
                issuer_perspective=False,
                at_issue=False,
                discount_rate=self.policy.policyholder_rate,
            )
        pv = pv_deathben - self.PV_repay(
            loanrate=loanrate,
            oneperiod_mort=oneperiod_mort,
            discount_rate=self.policy.policyholder_rate,
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
        if loanrate is np.nan:
            return 0
        in_flow = self.PV_repay(loanrate=loanrate, discount_rate=self.lender_coc)
        if not fullrecourse:
            if pv_deathben is None:
                pv_deathben = self.policy.PV_death_benefit(
                    issuer_perspective=None,
                    at_issue=False,
                    discount_rate=self.lender_coc,
                )
            in_flow = min(pv_deathben, in_flow)
        pv = in_flow - self.policy.PV_unpaid_premium(
            discount_rate=self.lender_coc, at_issue=False
        )
        return pv

    def PV_lender_maxed(
        self,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
    ) -> float:
        loanrate = self.max_loan_rate_borrower(fullrecourse=fullrecourse)
        pv = self.PV_lender(
            loanrate=loanrate,
            fullrecourse=fullrecourse,
            pv_deathben=pv_deathben,
        )
        return pv

    def surrender_value(self) -> float:

        variablepr = self.policy._variable_premium
        pr = self.policy.premium_stream_at_issue
        pr = make_list(pr)
        obs_period = self.policy.insured.current_age - self.policy.insured.issue_age

        cash_interest = self.policy.cash_interest
        surrender_value = 0
        for i in range(obs_period):
            surrender_value = (
                pr[i] - variablepr[i] + surrender_value * (1 + cash_interest)
            )

        return max(surrender_value, 0)

    def max_loan_rate_borrower(
        self,
        fullrecourse: bool = True,
    ) -> float:
        sv = self.surrender_value()
        # no lapse assumption for death benefit payment
        oneperiod_mort = self.policy.death_benefit_payment_probability(
            assume_lapse=False, at_issue=False
        )
        pv_deathben = self.policy.PV_death_benefit(
            issuer_perspective=False,
            at_issue=False,
            discount_rate=self.policy.policyholder_rate,
        )

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
