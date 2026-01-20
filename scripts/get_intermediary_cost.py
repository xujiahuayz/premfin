from premiumFinance.constants import DATA_FOLDER
from premiumFinance.financing import yield_curve
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured
from process_mortality_table import mortality_experience


def policy_fund_fees(
    issue_age: float,
    is_male: bool,
    is_smoker: bool,
    current_age: float,
    current_vbt: str = "VBT15",
    current_mort: float = 1.0,
    is_level_premium: bool = True,
    lapse_assumption: bool = True,
    policyholder_rate=yield_curve,
    statutory_interest: float = 0.035,
    premium_markup: float = 0.0,
    cash_interest: float = 0.03,
    annual_management_fee: float = 0.015,
    annual_performance_fee: float = 0.1,
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
    expected_management_fee = (
        sum(
            max(0, w)
            for w in this_policy.policy_value_future_list(
                at_issue=False, discount_rate=policyholder_rate, issuer_perspective=False
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


if "__main__" == __name__:

    EV = "Policy_EV_VBT01_lapseTrue_mort1_coihike_0"

    fees = {
        "life_settlement": {
            "broker_fee": 0.08,
            "management_fee": 0.015,
            "performance_fee": 0.1,
        },
    }

    for key, value in fees.items():
        BROKER_FEE = value["broker_fee"]
        MANAGEMENT_FEE = value["management_fee"]
        PERFORMANCE_FEE = value["performance_fee"]
        PROVIDER_FEE = 0.05

        mortality_experience['excess_TP']= [
            max(min(w,0.2),0) for w in (mortality_experience[EV] - mortality_experience["csv_rate"])
        ] 
        mortality_experience["buyer_pay"] = [
            max(w,0) for w in (mortality_experience["excess_TP"] + mortality_experience["csv_rate"])
        ] # if eev cant cover provider fee then probably not economic to sell
        #  0.2 is average settlement rate

# https://www.lisa.org/article_content.asp?edition=1&section=2&article=23
# 20% face value - policyholder gets
        mortality_experience["value_at_settlement"] = mortality_experience[EV] - mortality_experience["buyer_pay"]

        mortality_experience["broker_fee_rate"] = [
            max(min(w * 0.3, BROKER_FEE), 0)
            for w in (mortality_experience["excess_TP"])
        ]

        mortality_experience["policyholder_lump_sum"] = mortality_experience["buyer_pay"] - mortality_experience["broker_fee_rate"]

        mortality_experience["provider_fee_rate"] = [
            PROVIDER_FEE * w if w > 1e-6 else 0 for w in mortality_experience["buyer_pay"] 
        ] 

        mortality_experience[["management_fee_rate", "performance_fee_rate"]] = (
            mortality_experience.apply(
                lambda row: policy_fund_fees(
                    issue_age=row["issueage"],
                    is_male=row["isMale"],
                    is_smoker=row["isSmoker"],
                    current_age=row["currentage"],
                ) if row["value_at_settlement"] > 1e-6 else (0,0),
                axis=1,
                result_type="expand",
            )
        )

        # save mortality_experience to excel
        mortality_experience.to_excel(
            DATA_FOLDER / f"mortality_experience_{key}.xlsx", index=False
        )
