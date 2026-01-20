import pandas as pd

from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH
from premiumFinance.treasury_yield import yield_curve
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured

def policyholder_policy_value(
    issue_age: float,
    is_male: bool,
    is_smoker: bool,
    current_age: float,
    issue_vbt: str ="VBT01",
    current_vbt: str = "VBT15",
    current_mort: float = 1.0,
    is_level_premium=True,
    lapse_assumption=True,
    policyholder_rate=yield_curve,
    statutory_interest: float = 0.035,
    premium_markup: float = 0.0,
    cash_interest: float = 0.0,
    premium_hike: float = 0.0,
    # on pricing, policyholder rate doesn't matter
) -> tuple[float,float]:
    """
    calculate policy economic value in excess of its surrender value
    """
    this_insured = Insured(
        issue_age=issue_age,
        is_male=is_male,
        is_smoker=is_smoker,
        current_age=current_age,
        issue_vbt=issue_vbt,
        current_vbt=current_vbt,
        current_mortality_factor=current_mort,
    )

    # premium markup = 0 for default case to calculate
    this_policy = InsurancePolicy(
        insured=this_insured,
        is_level_premium=is_level_premium,
        lapse_assumption=lapse_assumption,
        statutory_interest=statutory_interest,
        premium_markup=premium_markup,
        policyholder_rate=policyholder_rate,
        cash_interest=cash_interest,
    )
    this_financing = PolicyFinancingScheme(policy=this_policy)
    sv = this_financing.surrender_value()

    this_policy.premium_stream_at_issue = [
        w * (1 + premium_hike) for w in this_policy.premium_stream_at_issue
    ]

    return (
        sv,
        this_policy.policy_value(
            issuer_perspective=False,
            at_issue=False,
            discount_rate=policyholder_rate,
        )
    )


mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

def generate_pv_column(
    issue_vbt: str = "VBT01",
    current_vbt: str = "VBT15",
    lapse_assumption: bool = True,
    current_mort: float = 1,
    premium_hike: float = 0.0,
):
    """
    generate columns of excess policy pv in different scenarios
    """
    col_name = f"Policy_EV_{issue_vbt}_lapse{lapse_assumption}_mort{current_mort}_coihike_{premium_hike}"

    # if col_name in mortality_experience.columns:
    #     print(col_name + " exists")
    #     return
    # else:
    #     print(col_name + " doesn't exist")
    mortality_experience[["csv_rate", col_name]] = mortality_experience.apply(
        lambda row: policyholder_policy_value(
            issue_age=row["issueage"],
            is_male=row["isMale"],
            is_smoker=row["isSmoker"],
            current_age=row["currentage"],
            issue_vbt=issue_vbt,
            current_vbt=current_vbt,
            policyholder_rate=yield_curve,
            lapse_assumption=lapse_assumption,
            current_mort=current_mort,
            premium_hike=premium_hike,
        ),
        axis=1,
        result_type="expand",
    )
    print(col_name + " generated")


if __name__ == "__main__":
    # generate_pv_column(
    #     issue_vbt="VBT15", lapse_assumption=True, current_mort=1, premium_hike=0
    # )
    generate_pv_column(
        issue_vbt="VBT01", lapse_assumption=True, current_mort=1, premium_hike=0
    )
    # generate_pv_column(
    #     issue_vbt="VBT01", lapse_assumption=False, current_mort=1, premium_hike=0
    # )
    # generate_pv_column(
    #     issue_vbt="VBT01", lapse_assumption=True, current_mort=0.5, premium_hike=0
    # )
    # generate_pv_column(
    #     issue_vbt="VBT01", lapse_assumption=True, current_mort=1, premium_hike=0.3
    # )

    mortality_experience.to_excel(MORTALITY_TABLE_CLEANED_PATH, index=False)
