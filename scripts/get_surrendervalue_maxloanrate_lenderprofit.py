from os import path
import pandas as pd

from premiumFinance.constants import (
    DATA_FOLDER,
    MORTALITY_TABLE_CLEANED_PATH,
)
from premiumFinance.financing import (
    calculate_lender_profit,
)

IRR_PATH = path.join(DATA_FOLDER, "irrs.xlsx")
PROFIT_PATH = path.join(DATA_FOLDER, "profits.xlsx")

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

# return 3 columns:
# surrender value
# breakeven loanrate -- i.e. max loan rate borrower / policyholder can accept
# lender profit at breakeven loanrate

profit_columns = mortality_experience.apply(
    lambda row: calculate_lender_profit(
        row=row,
    ),
    axis=1,
    result_type="expand",
)

profit_columns.to_excel(PROFIT_PATH, index=False)
