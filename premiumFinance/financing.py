from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from scipy import optimize

from premiumFinance.inspolicy import InsurancePolicy, make_list
from premiumFinance.insured import Insured
from premiumFinance.treasury_yield import yield_curve
from premiumFinance.util import cash_flow_pv

from matplotlib import pyplot as plt


@dataclass
class PolicyFinancingScheme:
    """
    define all financing related methods of a particular policy
    """

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

    def PV_repay_list(
        self,
        loanrate: float,
        discount_rate: Any,
        oneperiod_mort: Any = None,
    ) -> list[float]:
        pr = make_list(self.unpaid_pr())

        # Note: every repay element corresponds to mortality rate,
        # i.e. the repay amount when you DIE at the beginning of a period (given survival last period)
        # therefore, DO NOT include this period's premium!
        cumulative_loan = 0.0
        loan_cash_flow = [cumulative_loan]
        for w in pr:
            cumulative_loan = (cumulative_loan + w) * (1 + loanrate)
            loan_cash_flow.append(cumulative_loan)

        if oneperiod_mort is None:
            # investor / policyholder usually does not assume lapse
            oneperiod_mort = self.policy.death_benefit_payment_probability(
                assume_lapse=False, at_issue=False
            )

        # change note: no need anymore as this has been considered under the Mortality class
        # # this is to make sure that unconditional mortality rate in the end converges to 0!!
        # oneperiod_mort = oneperiod_mort + [0.0] * 250

        return cash_flow_pv(
            cashflow=loan_cash_flow,
            probabilities=oneperiod_mort,
            discounters=discount_rate,
        )

    def PV_repay(
        self,
        loanrate: float,
        discount_rate: Any,
        oneperiod_mort: Any = None,
    ) -> float:
        cash_stream = self.PV_repay_list(
            loanrate=loanrate,
            discount_rate=discount_rate,
            oneperiod_mort=oneperiod_mort,
        )

        return sum(cash_stream)

    def PV_borrower(
        self,
        loanrate: float,
        fullrecourse: bool = True,
        pv_deathben: float | None = None,
        oneperiod_mort: Any = None,
    ) -> float:
        if pv_deathben is None:
            pv_deathben = self.policy.pv_death_benefit(
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
        pv_deathben: float | None = None,
    ) -> float:
        if loanrate is np.nan:
            return 0
        in_flow = self.PV_repay(loanrate=loanrate, discount_rate=self.lender_coc)
        if not fullrecourse:
            if pv_deathben is None:
                pv_deathben = self.policy.pv_death_benefit(
                    issuer_perspective=None,
                    at_issue=False,
                    discount_rate=self.lender_coc,
                )
            in_flow = min(pv_deathben, in_flow)
        pv = in_flow - self.policy.pv_unpaid_premium(
            discount_rate=self.lender_coc, at_issue=False
        )
        return pv

    def PV_lender_maxed(
        self,
        fullrecourse: bool = True,
        pv_deathben: float | None = None,
    ) -> float:
        _, loanrate = self.max_loan_rate_borrower(fullrecourse=fullrecourse)
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
        for i in range(int(obs_period)+1):
            surrender_value = (
                pr[i] - variablepr[i] + surrender_value * (1 + cash_interest)
            )

        return max(surrender_value * (1 - self.policy.surrender_penalty_rate), 0)

    
    def break_even_premium_increase(self) -> float:
        """
        break-even premium increase that would make the policy value equal to surrender value
        """
        surrender_value = self.surrender_value()
        # root find the increase that would make the policy value equal to surrender value
        sol = optimize.root_scalar(
            lambda increase: self.policy.policy_value(
                premium_stream_at_issue=self.policy._level_premium * (1+increase),
                issuer_perspective=False,
                at_issue=False,
                discount_rate=self.policy.policyholder_rate,
            ) - surrender_value,
            x0=0.01,
            bracket=[0, 100],
            method="brentq",
        )
        return sol.root

    def policyholder_IRR(
        self,
    ) -> list:
        sv = self.surrender_value()
        # no lapse assumption for death benefit payment
        sol = optimize.root_scalar(
            lambda r: sv
            + self.policy.policy_value(
                issuer_perspective=False,
                at_issue=False,
                discount_rate=r,
            ),
            x0=0.1,
            bracket=[-0.6, 99],
            method="brentq",
        )
        return sol.root

        # sols = []
        # interval = 0.05
        # for i in range(100):
        #     range_a = i * interval - 0.5
        #     arange = [range_a, range_a + interval]
        #     try:
        #         sol = optimize.root_scalar(
        #             lambda r: sv
        #             + self.policy.policy_value(
        #                 issuer_perspective=False,
        #                 at_issue=False,
        #                 discount_rate=r,
        #             ),
        #             x0=np.mean(arange),
        #             bracket=arange,
        #             method="brentq",
        #         )
        #         sols.append(sol.root)
        #     except:
        #         next
        # return sols

    def max_loan_rate_borrower(
        self,
        fullrecourse: bool = True,
    ) -> tuple[float, float]:
        sv = self.surrender_value()
        # no lapse assumption for death benefit payment
        oneperiod_mort = self.policy.death_benefit_payment_probability(
            assume_lapse=False, at_issue=False
        )
        pv_deathben = self.policy.pv_death_benefit(
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
        return sv, sol.root


def calculate_lender_profit(
    row,
    current_vbt="VBT15",
    current_mort=1.0,
    is_level_premium=True,
    lapse_assumption=True,
    policyholder_rate=yield_curve,
    statutory_interest=0.035,
    premium_markup=0.0,
    cash_interest=0.03,
    lender_coc=0.01,
) -> tuple[float, float, float]:
    this_insured = Insured(
        issue_age=row["issueage"],  # type: ignore
        is_male=row["isMale"],  # type: ignore
        is_smoker=row["isSmoker"],  # type: ignore
        current_age=row["currentage"],  # type: ignore
        issue_vbt="VBT01",
        current_vbt=current_vbt,
        current_mortality_factor=current_mort,
    )
    this_policy = InsurancePolicy(
        insured=this_insured,
        is_level_premium=is_level_premium,
        lapse_assumption=lapse_assumption,
        statutory_interest=statutory_interest,
        premium_markup=premium_markup,
        policyholder_rate=policyholder_rate,
        cash_interest=cash_interest,
    )
    this_financing = PolicyFinancingScheme(this_policy, lender_coc=lender_coc)
    this_sv, this_breakeven_loanrate = this_financing.max_loan_rate_borrower(
        fullrecourse=True
    )
    if not (0.0 < this_breakeven_loanrate < 1.0):
        this_breakeven_loanrate = np.nan
        this_lender_profit = 0.0
        # else:
    elif isinstance(lender_coc, (int, float)) and this_breakeven_loanrate <= lender_coc:
        this_lender_profit = 0.0
    else:
        this_lender_profit = this_financing.PV_lender(
            loanrate=this_breakeven_loanrate, fullrecourse=True
        )
    return this_sv, this_breakeven_loanrate, max(this_lender_profit, 0.0)
    # return this_sv, this_breakeven_loanrate, this_lender_profit


def calculate_policyholder_IRR(
    row,
    currentVBT: str = "VBT15",
    currentmort: float = 1.0,
    is_level_premium: bool = True,
    lapse_assumption: bool = True,
    policyholder_rate: float | Iterable[float] = yield_curve,
    statutory_interest=0.035,
    premium_markup=0.0,
    cash_interest=0.03,
    lender_coc=0.01,
) -> float:
    this_insured = Insured(
        issue_age=row["issueage"],  # type: ignore
        is_male=row["isMale"],  # type: ignore
        is_smoker=row["isSmoker"],  # type: ignore
        current_age=row["currentage"],  # type: ignore
        issue_vbt="VBT01",
        current_vbt=currentVBT,
        current_mortality_factor=currentmort,
    )
    this_policy = InsurancePolicy(
        insured=this_insured,
        is_level_premium=is_level_premium,
        lapse_assumption=lapse_assumption,
        statutory_interest=statutory_interest,
        premium_markup=premium_markup,
        policyholder_rate=policyholder_rate,
        cash_interest=cash_interest,
    )
    this_financing = PolicyFinancingScheme(this_policy, lender_coc=lender_coc)
    try:
        irr = this_financing.policyholder_IRR()
    except ValueError:
        print(row)
        irr = np.nan
    return irr


if __name__ == "__main__":

    for issue_age in [35, 50, 65, 80]:

        increases = []
        current_ages = np.arange(issue_age, 100, 5)

        for current_age in current_ages:
            this_scheme = PolicyFinancingScheme(
                policy=InsurancePolicy(
                    insured=Insured(
                        issue_age=issue_age,
                        is_male=True,
                        is_smoker=False,
                        current_age=current_age,
                    ),
                    is_level_premium=True,
                )
            )
            increase = this_scheme.break_even_premium_increase()
            print(f"current age: {current_age}, increase: {increase}")
            increases.append(increase)
        # plot current age vs increase
        plt.plot(current_ages, increases)
        plt.xlabel("current age")
        plt.title(f"issue age: {issue_age}")
        plt.show()