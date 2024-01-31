from typing import Iterable
from scipy import optimize
from matplotlib import pyplot as plt

from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured
from premiumFinance.treasury_yield import yield_curve
from premiumFinance.util import cash_flow_pv

from scripts.process_mortality_table import mortality_experience


def cundiscounted_cash_flow(
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
) -> list[float]:
    this_insured = Insured(
        issue_age=row["issueage"],  # type: ignore
        is_male=row["isMale"],  # type: ignore
        is_smoker=row["isSmoker"],  # type: ignore
        current_age=row["currentage"],  # type: ignore
        issue_vbt="VBT01",
        current_vbt=currentVBT,
        current_mort=currentmort,
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
    return this_financing.policy.policy_value_list(
        issuer_perspective=False,
        at_issue=False,
        discount_rate=0,
    )


probablistic_cash_flows = mortality_experience.apply(
    lambda row: [
        -w * row["Amount Exposed"]
        for w in cundiscounted_cash_flow(
            row=row,
        )
    ],
    axis=1,
    result_type="expand",
)

# for each column, sum all the rows where mortality_experience[life_expectancy] <20
aggregated_cash_flow = probablistic_cash_flows[
    mortality_experience["life_expectancy"] < 1000
].sum(axis=0)

plt.bar(x=range(len(aggregated_cash_flow)), height=aggregated_cash_flow)

sol = optimize.root_scalar(
    lambda r: sum(
        cash_flow_pv(
            cashflow=aggregated_cash_flow,
            probabilities=1,
            discounters=r,
        )
    ),
    x0=0.1,
    bracket=[-0.6, 99],
    method="brentq",
)
