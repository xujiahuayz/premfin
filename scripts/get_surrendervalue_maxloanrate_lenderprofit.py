#%%
import pandas as pd

from premiumFinance.constants import (
    DATA_FOLDER,
    MORTALITY_TABLE_CLEANED_PATH,
)
from premiumFinance.financing import (
    calculate_lender_profit,
)


mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)
#%%
# return 3 columns:
# surrender value
# breakeven loanrate -- i.e. max loan rate borrower / policyholder can accept
# lender profit at breakeven loanrate
mortality_experience.apply(
    lambda row: calculate_lender_profit(
        row=row,
    ),
    axis=1,
    result_type="expand",
)
