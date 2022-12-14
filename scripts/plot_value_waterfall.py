"""
Plot value lost waterfall
"""
import plotly.graph_objects as go

from scripts.plot_moneyleft import (
    sample_representativeness,
    money_left_15_T,
    mortality_experience,
)
from premiumFinance.financing import yield_curve
from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy


# def broker_fee_rate(
#     excess_value: float,
#     excess_value_rate: float = 0.3,
#     face_vale_rate: float = 0.08,
# ):
#     """
#     calculate broker fee,
#     which by default is the lesser of
#     30% excess value and 8% face
#     """
#     return min(excess_value * excess_value_rate, face_vale_rate)


def policy_fund_fees(
    issue_age: float,
    is_male: bool,
    is_smoker: bool,
    current_age: float,
    current_vbt: str = "VBT15",
    current_mort: float = 1.0,
    is_level_premium=True,
    lapse_assumption=True,
    policyholder_rate=yield_curve,
    statutory_interest: float = 0.035,
    premium_markup: float = 0.0,
    cash_interest: float = 0.03,
    annual_management_fee: float = 0.01,
    annual_performance_fee: float = 0.15,
) -> tuple[float, float]:
    """
    calculate the sum of all future probabilistic pv-discounted navs
    """

    this_insured = Insured(
        issue_age=issue_age,
        is_male=is_male,
        is_smoker=is_smoker,
        current_age=current_age,
        issue_vbt="VBT01",
        current_vbt=current_vbt,
        current_mort=current_mort,
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
    expected_management_fee = (
        sum(
            max(0, -w)
            for w in this_policy.policy_value_future_list(
                at_issue=False, discount_rate=policyholder_rate
            )
        )
        * annual_management_fee
    )

    expected_performance_fee = (
        sum(
            max(0, w)
            for w in this_policy.nav_gain(
                at_issue=False, discount_rate=policyholder_rate
            )
        )
        * annual_performance_fee
    )
    return expected_management_fee, expected_performance_fee


mortality_experience["broker_fee_rate"] = [
    max(min(w * 0.3, 0.08), 0)
    for w in mortality_experience["Excess_Policy_PV_VBT15_lapseTrue_mort1_coihike_0"]
]


mortality_experience[
    ["management_fee_rate", "performance_fee_rate"]
] = mortality_experience.apply(
    lambda row: policy_fund_fees(
        issue_age=row["issueage"],
        is_male=row["isMale"],
        is_smoker=row["isSmoker"],
        current_age=row["currentage"],
    ),
    axis=1,
    result_type="expand",
)

broker_fee = (
    sum(
        mortality_experience["broker_fee_rate"] * mortality_experience["Amount Exposed"]
    )
    * sample_representativeness
)

management_fee = (
    sum(
        mortality_experience["management_fee_rate"]
        * mortality_experience["Amount Exposed"]
    )
    * sample_representativeness
)

performance_fee = (
    sum(
        mortality_experience["performance_fee_rate"]
        * mortality_experience["Amount Exposed"]
    )
    * sample_representativeness
)

policyholder_lump_sum = (
    0.18 * sum(mortality_experience["Amount Exposed"]) * sample_representativeness
) - broker_fee


fig = go.Figure(
    go.Waterfall(
        name="20",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=[
            "Life insurance value to policyholders",
            "Policyholder lump sum",
            "Broker fee",
            "Management fee",
            "Performance fee",
            "Investor profit",
        ],
        textposition="outside",
        # text=[
        #     money_left_15_T,
        #     policyholder_lump_sum,
        #     broker_fee,
        #     management_fee,
        #     performance_fee,
        #     "Total",
        # ],
        y=[
            money_left_15_T,
            -policyholder_lump_sum,
            -broker_fee,
            -management_fee,
            -performance_fee,
            0,
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    )
)

fig.update_layout(title="Profit and loss statement 2018", showlegend=True)

fig.show()

money_left_15_T / 1e12
(
    policyholder_lump_sum / 1e12
    + broker_fee / 1e12
    + management_fee / 1e12
    + performance_fee / 1e12
)
