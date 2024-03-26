from typing import Iterable

from matplotlib import pyplot as plt
from scipy import optimize

from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured
from premiumFinance.treasury_yield import yield_curve
from premiumFinance.util import cash_flow_pv
from scripts.process_aapartners import aapartners_grouped
from scripts.process_mortality_table import (
    mortality_experience,
    sample_representativeness,
)

# based on mortality_experience['isMale'], get 'tp_rate' from aapartners_grouped
mortality_experience["tp_rate"] = mortality_experience["isMale"].map(
    lambda x: aapartners_grouped.loc[x, "tp_rate"]
)


def condiscounted_cash_flow(
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


probablistic_cash_flows_rate = mortality_experience.apply(
    lambda row: [
        -w
        for w in condiscounted_cash_flow(
            row=row,
        )
    ],
    axis=1,
    result_type="expand",
)


## deduct transaction cost for column 0
probablistic_cash_flows_rate[0] -= mortality_experience["tp_rate"]

# for each row, multiply rate by amount exposed, lapse_rate and sample_representativeness

probablistic_cash_flows = probablistic_cash_flows_rate.mul(
    mortality_experience["Amount Exposed"]
    # * mortality_experience["lapse_rate"]
    * sample_representativeness,
    axis=0,
)

# # deduct transaction cost for column 0
probablistic_cash_flows[0] -= (
    mortality_experience["Amount Exposed"]
    * mortality_experience["tp_rate"]
    # * 0.01
)

for ranges in [(0, 100), (0, 20), (0, 30), (20, 50), (50, 100)]:

    aggregated_cash_flow = probablistic_cash_flows[
        mortality_experience["life_expectancy"].between(*ranges)
    ].sum(axis=0)

    # calculate Macaulay Duration using the aggregated cash flow and yield curve
    pv_cash_flow = cash_flow_pv(
        cashflow=aggregated_cash_flow, probabilities=1, discounters=yield_curve
    )
    time_weighted_cash_flow = [t * c for t, c in enumerate(pv_cash_flow, start=0)]
    macaulay_duration = sum(time_weighted_cash_flow) / sum(pv_cash_flow)

    plt.bar(
        x=range(len(aggregated_cash_flow)),
        height=aggregated_cash_flow,
        alpha=0.5,
    )

    plt.xlabel("Year since portfolio establishment")
    plt.ylabel("Cash flow")
    plt.xlim(-2, 87)

    sol = optimize.root_scalar(
        lambda r: sum(
            cash_flow_pv(cashflow=aggregated_cash_flow, probabilities=1, discounters=r)
        ),
        x0=0.1,
        bracket=[-0.6, 2],
        method="brentq",
    )

    # add text on the top right corner of the plot
    plt.text(
        0.8,
        0.9,
        f"LE range: {ranges} \n IRR: {sol.root*100:.2f}% \n Macaulay Duration: {macaulay_duration:.2f}",
        horizontalalignment="center",
        verticalalignment="center",
        transform=plt.gca().transAxes,
    )
    plt.show()
