from premiumFinance.financing import (
    yield_curve,
    policyholder_policy_value,
    calculate_lender_profit,
)

from premiumFinance.fetchdata import getMarketSize
from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH

import pandas as pd
from scipy import optimize

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)


sample_representativeness = (
    getMarketSize(year=2020) / mortality_experience["Amount Exposed"].sum()
)


def findMoneyleft(currentmort, row, currentVBT, lapse_assup):
    profit_columns = calculate_lender_profit(
        row=row,
        current_vbt=currentVBT,
        lapse_assumption=lapse_assup,
        current_mort=currentmort,
    )
    row["policy_value"] = (
        policyholder_policy_value(
            row=row,
            current_vbt=currentVBT,
            policyholder_rate=yield_curve,
            lapse_assumption=lapse_assup,
            currentmort=currentmort,
        )
        - profit_columns[0]
    )
    money_left = row["policy_value"] * row["Amount Exposed"] * sample_representativeness
    return money_left


def findEvenMortrate(row, currentVBT, lapse_assup, bracket):
    result = optimize.root_scalar(
        lambda r: findMoneyleft(
            currentmort=r,
            row=row,
            lapse_assup=lapse_assup,
            currentVBT=currentVBT,
        ),
        bracket=bracket,
        method="brentq",
    )
    return result.root
