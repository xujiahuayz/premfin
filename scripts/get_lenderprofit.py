# %% import packages

import json
import multiprocessing
from time import time

import numpy as np
import pandas as pd

from premiumFinance.constants import (
    MORTALITY_TABLE_CLEANED_PATH,
    PROCESSED_PROFITABILITY_PATH,
)
from premiumFinance.financing import calculate_lender_profit, yield_curve

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)


# %% calculate profit rate
def get_average_profitability(
    is_level_premium: bool = True,
    lapse_assumption: bool = True,
    policyholder_rate: float | np.ndarray = yield_curve,
    statutory_interest: float = 0.035,
    premium_markup: float = 0.0,
    cash_interest: float = 0.001,
    lender_coc: float = 0.01,
    data_frame: pd.DataFrame = mortality_experience,
) -> tuple[float, pd.DataFrame]:
    profit_columns = data_frame.apply(
        lambda row: calculate_lender_profit(
            row=row,
            is_level_premium=is_level_premium,
            lapse_assumption=lapse_assumption,
            policyholder_rate=policyholder_rate,
            statutory_interest=statutory_interest,
            premium_markup=premium_markup,
            cash_interest=cash_interest,
            lender_coc=lender_coc,
        ),
        axis=1,
        result_type="expand",
    )
    data_frame[["Breakeven Loan rate", "Lender profit"]] = profit_columns

    data_frame["Dollar profit"] = (
        data_frame["Lender profit"] * data_frame["Amount Exposed"]
    )

    average_profitability = (
        data_frame["Dollar profit"].sum() / data_frame["Amount Exposed"].sum()
    )
    return average_profitability, data_frame


def tempfunc_t(x):
    a, _ = get_average_profitability(lender_coc=x, lapse_assumption=True)
    return a


def tempfunc_f(x):
    a, _ = get_average_profitability(lender_coc=x, lapse_assumption=False)
    return a


lender_coc_value = np.arange(start=0.01, stop=0.2, step=0.01)


# %% tbd
if __name__ == "__main__":
    pool = multiprocessing.Pool()

    start_time = time()
    foo = []
    for tempfunc in (tempfunc_t, tempfunc_f):
        foo.append(
            pool.map(
                tempfunc,
                lender_coc_value,
            )
        )
    print(f"it took {time() - start_time}")
    lender_profitability = {
        "lender_coc": lender_coc_value.tolist(),
        "profitability": foo,
    }
    with open(PROCESSED_PROFITABILITY_PATH, "w") as outfile:
        json.dump(lender_profitability, outfile)

# %%
