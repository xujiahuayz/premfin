#%%
from os import path
import pandas as pd

from premiumFinance.constants import (
    DATA_FOLDER,
    MORTALITY_TABLE_CLEANED_PATH,
)
from premiumFinance.financing import (
    calculate_lender_profit,
)
#%%
IRR_PATH = path.join(DATA_FOLDER, "irrs.xlsx")
PROFIT_PATH = path.join(DATA_FOLDER, "profits.xlsx")
PROFIT_PATH_cnt = path.join(DATA_FOLDER,"profits_cnt.xlsx")
PROFIT_PATH_cnt_false = path.join(DATA_FOLDER,"profits_cnt_false.xlsx")
PROFIT_PATH_cnt_15_T_mort5 = path.join(DATA_FOLDER,"profits_cnt_15_T_0.5.xlsx")
PROFIT_PATH_cnt_15_T_mort3 = path.join(DATA_FOLDER, "profits_cnt_15_T_0.3.xlsx")
PROFIT_PATH_cnt_15_T_mort03 = path.join(DATA_FOLDER, "profits_cnt_15_T_0.03.xlsx")
PROFIT_PATH_cnt_15_T_mort05 = path.join(DATA_FOLDER, "profits_cnt_15_T_0.05.xlsx")
mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)
#%%
# return 3 columns:
# surrender value
# breakeven loanrate -- i.e. max loan rate borrower / policyholder can accept
# lender profit at breakeven loanrate
def get_profit_columns(currentVBT,lapse_assup,currentmort=1.0):
    profit_columns = mortality_experience.apply(
        lambda row: calculate_lender_profit(
            row=row,
            currentVBT=currentVBT,
            lapse_assumption=lapse_assup,
            currentmort=currentmort
        ),
        axis=1,
        result_type="expand",
    )
    return profit_columns
#%%
profit_columns=get_profit_columns(currentVBT="VBT15", lapse_assup=True)
profit_columns.to_excel(PROFIT_PATH, index=False)
#%%
profit_columns=get_profit_columns(currentVBT="VBT01", lapse_assup=True)
profit_columns.to_excel(PROFIT_PATH_cnt,index=False)
#%%
profit_columns=get_profit_columns(currentVBT="VBT15", lapse_assup=False)
profit_columns.to_excel(PROFIT_PATH_cnt_false, index=False)

# %%
profit_columns=get_profit_columns(currentVBT="VBT15", lapse_assup=True,currentmort=0.5)
profit_columns.to_excel(PROFIT_PATH_cnt_15_T_mort5, index=False)
# %%
profit_columns = get_profit_columns(currentVBT="VBT15",lapse_assup=True,currentmort=0.3)
profit_columns.to_excel(PROFIT_PATH_cnt_15_T_mort3,index=False)
# %%
profit_columns = get_profit_columns(currentVBT="VBT15",lapse_assup=True,currentmort=0.03)
profit_columns.to_excel(PROFIT_PATH_cnt_15_T_mort03,index=False)
# %%
profit_columns = get_profit_columns(currentVBT="VBT15",lapse_assup=True,currentmort=0.05)
profit_columns.to_excel(PROFIT_PATH_cnt_15_T_mort05,index=False)
# %%
