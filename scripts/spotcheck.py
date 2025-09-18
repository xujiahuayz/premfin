from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy
import pandas as pd
import itertools 


# check against: https://www.forbes.com/advisor/life-insurance/universal-life-insurance/
# https://web.archive.org/web/20200323151921/https://www.forbes.com/advisor/life-insurance/universal-life-insurance/
# the numbers are from Mar 8, 2020

def spot_check_premium(lapse_assumption: bool, gender: bool, age: int) -> float:
    insrd_benchmark = Insured(
        issue_age=age,
        is_male=gender,
        is_smoker=False,
        current_age=age,
        issue_mortality_factor=1.0,
        current_mortality_factor=1.0,
        issue_vbt="VBT15",
        current_vbt="VBT15",
    )

    insPol = InsurancePolicy(
        insured=insrd_benchmark,
        is_level_premium=True,
        lapse_assumption=lapse_assumption,
        premium_markup= 0,
        surrender_penalty_rate = 0.2,
        cash_interest = 0.0,
        statutory_interest= 0.035,
    )

    return insPol._level_premium
    

# forbes data is old https://web.archive.org/web/20200323151921/https://www.forbes.com/advisor/life-insurance/universal-life-insurance/

if __name__ == "__main__":
    # for (lapse_assumption, gender, age) in zip(
    #     [True, False], [True, False], [30, 35, 40, 45, 50, 55, 60]
    # ):
    #     spot_check_premium(lapse_assumption=lapse_assumption, gender=gender, age=age)
    results = []
    for lapse_assumption, gender, age in itertools.product(
        [True, False], [True, False], [30, 35, 40, 45, 50, 55, 60]
    ):
        results.append({
            'age': age,
            'gender': 'Male' if gender else 'Female',
            "lapse_assumption": lapse_assumption,
            "premium": round(spot_check_premium(lapse_assumption=lapse_assumption, gender=gender, age=age) * 1e6)
        }
        )
    df = pd.DataFrame(results)
    print(df)
            

