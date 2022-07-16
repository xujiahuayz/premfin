import pandas as pd

from premiumFinance.constants import (
    MORTALITY_TABLE_CLEANED_PATH,
)
from premiumFinance.financing import PolicyFinancingScheme, yield_curve
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured


def policyholder_policy_value(
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
    # TODO: check a realistic cash interest from 2010-2015
    # 4% P.9: 3.5% p18 https://www.dropbox.com/s/rnf0k84744xj9xe/Policy_A10.pdf?dl=0
    # 2-3.75% P.7 https://www.dropbox.com/s/tieqon4l3znfqco/Illustration_A6.pdf?dl=0
    cash_interest: float = 0.03,
) -> float:
    """
    calculate policy economic value in excess of its surrender value
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
    this_financing = PolicyFinancingScheme(policy=this_policy)
    return (
        -this_policy.policy_value(
            issuer_perspective=False,
            at_issue=False,
            discount_rate=policyholder_rate,
        )
        - this_financing.surrender_value()
    )


mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)


def generate_pv_column(
    current_vbt: str = "VBT15", lapse_assumption: bool = True, current_mort: float = 1
):
    """
    generate columns of excess policy pv in different scenarios
    """
    col_name = (
        f"Excess_Policy_PV_{current_vbt}_lapse{lapse_assumption}_mort{current_mort}"
    )

    if col_name in mortality_experience.columns:
        print(col_name + " exists")
        return
    else:
        print(col_name + " doesn't exist")
    mortality_experience[col_name] = mortality_experience.apply(
        lambda row: policyholder_policy_value(
            issue_age=row["issueage"],
            is_male=row["isMale"],
            is_smoker=row["isSmoker"],
            current_age=row["currentage"],
            current_vbt=current_vbt,
            policyholder_rate=yield_curve,
            lapse_assumption=lapse_assumption,
            current_mort=current_mort,
        ),
        axis=1,
        result_type="expand",
    )
    print(col_name + " generated")


if __name__ == "__main__":
    generate_pv_column(current_vbt="VBT01", lapse_assumption=True, current_mort=1)
    generate_pv_column(current_vbt="VBT15", lapse_assumption=True, current_mort=1)
    generate_pv_column(current_vbt="VBT15", lapse_assumption=False, current_mort=1)
    generate_pv_column(current_vbt="VBT15", lapse_assumption=True, current_mort=0.5)

    mortality_experience.to_excel(MORTALITY_TABLE_CLEANED_PATH, index=False)
