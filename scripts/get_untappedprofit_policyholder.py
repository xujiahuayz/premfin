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
PROFIT_PATH_cnt = path.join(DATA_FOLDER, "profits_cnt.xlsx")
PROFIT_PATH_cnt_false = path.join(DATA_FOLDER, "profits_cnt_false.xlsx")
PROFIT_PATH_cnt_15_T_mort5 = path.join(DATA_FOLDER, "profits_cnt_15_T_0.5.xlsx")
PROFIT_PATH_cnt_15_T_mort3 = path.join(DATA_FOLDER,"profits_cnt_15_T_0.3.xlsx")
PROFIT_PATH_cnt_15_T_mort03 = path.join(DATA_FOLDER, "profits_cnt_15_T_0.03.xlsx")
PROFIT_PATH_cnt_15_T_mort05 = path.join(DATA_FOLDER, "profits_cnt_15_T_0.05.xlsx")
#%% calculate policy PV from perspective of policyholder in excess of surrender value
def get_untappedprofit(profitpath: str, mortality_experience: pd.DataFrame, currentVBT : str, lapse_assup,currentmort=1.0):
    mortality_experience["Excess_Policy_PV_yield_curve"] = (
        mortality_experience.apply(
            lambda row: policyholder_policy_value(
                row=row, currentVBT=currentVBT, policyholder_rate=yield_curve,lapse_assumption=lapse_assup,currentmort=currentmort
            ),
            axis=1,
            result_type="expand",
        )
        - pd.read_excel(profitpath)[0]
    )

    for i in [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
        print(i)
        mortality_experience[f"Excess_Policy_PV_{i}"] = (
            mortality_experience.apply(
                lambda row: policyholder_policy_value(
                    row=row, currentVBT=currentVBT, policyholder_rate=i, lapse_assumption=lapse_assup,currentmort=currentmort
                ),
                axis=1,
                result_type="expand",
            )
            - pd.read_excel(profitpath)[0]
        )

    #%% post-process

    profit_columns = pd.read_excel(profitpath)
    mortality_experience[
        ["Surrender value", "Max Loan rate", "Lender profit"]
    ] = profit_columns

    mortality_experience["Dollar profit"] = (
        mortality_experience["Lender profit"] * mortality_experience["Amount Exposed"]
    )
    return mortality_experience


#%% currentVBT set to "VBT15"
mortality_experience = get_untappedprofit(PROFIT_PATH, mortality_experience, currentVBT="VBT15",lapse_assup=True)
untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)

#%% currentVBT set to "VBT01"
mortality_experience = get_untappedprofit(PROFIT_PATH_cnt, mortality_experience, currentVBT="VBT01",lapse_assup=True)
untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit_cnt.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
#%% currentVBT set to "VBT15"
mortality_experience = get_untappedprofit(PROFIT_PATH_cnt_false, mortality_experience, "VBT15",lapse_assup=False)
untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit_cnt_false.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
#%% currentVBT set to "VBT15", mort_rate = 0.5
mortality_experience = get_untappedprofit(PROFIT_PATH_cnt_15_T_mort5, mortality_experience, currentVBT="VBT15",lapse_assup=True,currentmort=0.5)
untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit_cnt_15_T_mort5.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
# %% currentVBT set to "VBT15", mort_rate = 0.3
mortality_experience = get_untappedprofit(PROFIT_PATH_cnt_15_T_mort3, mortality_experience, currentVBT="VBT15",lapse_assup=True,currentmort=0.3)
untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit_cnt_15_T_mort3.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
# %% currentVBT set to "VBT15", mort_rate = 0.03
mortality_experience = get_untappedprofit(PROFIT_PATH_cnt_15_T_mort03, mortality_experience, currentVBT="VBT15",lapse_assup=True,currentmort=0.03)
untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit_cnt_15_T_mort03.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
# %% currentVBT set to "VBT15", mort_rate = 0.05
mortality_experience = get_untappedprofit(PROFIT_PATH_cnt_15_T_mort05, mortality_experience, currentVBT="VBT15",lapse_assup=True,currentmort=0.03)
untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit_cnt_15_T_mort05.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
# %%
