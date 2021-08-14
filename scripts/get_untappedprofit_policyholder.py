#%% import packages
from os import path
import pandas as pd

from premiumFinance.constants import (
    DATA_FOLDER,
    MORTALITY_TABLE_CLEANED_PATH,
)
from premiumFinance.financing import (
    yield_curve,
    policyholder_policy_value,
)

PROFIT_PATH = path.join(DATA_FOLDER, "profits.xlsx")
mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

#%% calculate policy PV from perspective of policyholder

mortality_experience["Excess_Policy_PV_yield_curve"] = (
    mortality_experience.apply(
        lambda row: policyholder_policy_value(row=row, policyholder_rate=yield_curve),
        axis=1,
        result_type="expand",
    )
    - pd.read_excel(PROFIT_PATH)[0]
)

for i in [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
    print(i)
    mortality_experience[f"Excess_Policy_PV_{i}"] = (
        mortality_experience.apply(
            lambda row: policyholder_policy_value(row=row, policyholder_rate=i),
            axis=1,
            result_type="expand",
        )
        - pd.read_excel(PROFIT_PATH)[0]
    )

#%% post-process

profit_columns = pd.read_excel(PROFIT_PATH)
mortality_experience[
    ["Surrender value", "Max Loan rate", "Lender profit"]
] = profit_columns

mortality_experience["Dollar profit"] = (
    mortality_experience["Lender profit"] * mortality_experience["Amount Exposed"]
)

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
