from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy


# check against: https://www.forbes.com/advisor/life-insurance/universal-life-insurance/
def spot_check_premium(gender: bool, age: int):
    insrd_benchmark = Insured(
        issue_age=age,
        is_male=gender,
        is_smoker=False,
        current_age=age,
        issue_mort=1.0,
        current_mort=1.0,
        issue_vbt="VBT01",
        current_vbt="VBT15",
    )

    insPol = InsurancePolicy(
        insured=insrd_benchmark,
        is_level_premium=True,
        lapse_assumption=True,
    )

    print(
        f"gender: {'Male' if gender else 'Female'}\n age: {age}\n premium: {insPol._level_premium}"
    )


if __name__ == "__main__":
    for gender in [True, False]:
        for age in [30, 35, 40, 45, 50, 55, 60]:
            spot_check_premium(gender=gender, age=age)
