import pandas as pd

from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH
from premiumFinance.financing import calculate_lender_profit


mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)
# return 3 columns:
# surrender value
# breakeven loanrate -- i.e. max loan rate borrower / policyholder can accept
# lender profit at breakeven loanrate
mortality_experience[["surrender_value", "breakeven_loan_rate", "lender_profit"]] = (
    mortality_experience.apply(
        lambda row: calculate_lender_profit(
            row=row,
            current_vbt="VBT15",
            current_mort=1.0,
            is_level_premium=True,
            lapse_assumption=True,
            statutory_interest=0.035,
            premium_markup=0.0,
            cash_interest=0.03,
            lender_coc=0.01,
        ),
        axis=1,
        result_type="expand",
    )
)

mortality_experience.to_excel(MORTALITY_TABLE_CLEANED_PATH, index=False)
