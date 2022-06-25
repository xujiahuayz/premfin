from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy


# check against: https://www.forbes.com/advisor/life-insurance/universal-life-insurance/
def spot_check_premium(gender: bool, age: int):
    insrd_benchmark = Insured(
        issue_age=age,
        isMale=gender,
        isSmoker=False,
        current_age=age,
        issuemort=1.0,
        currentmort=1.0,
        issueVBT="VBT01",
        currentVBT="VBT15",
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
