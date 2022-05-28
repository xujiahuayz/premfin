from typing import Union
import numpy as np
import pandas as pd
from premiumFinance.fetchdata import lapse_tbl
from typing import List

LIST_LEN = 150
# make a list with length 150
def make_list(x, to_length: int = LIST_LEN) -> List[float]:
    if type(x) == np.ndarray:
        x = x.tolist()
    elif type(x) == pd.Series:
        x = x.to_list()
    elif isinstance(x, (int, float)):
        x = [float(x)]
    x_lenghth = len(x)
    if x_lenghth < to_length:
        x.extend([x[-1]] * (to_length - x_lenghth))
    else:
        x = x[:to_length]
    return x


def cash_flow_pv(
    cashflow: Union[float, List[float], np.ndarray, pd.Series],
    probabilities: Union[float, List[float], np.ndarray, pd.Series],
    discounters: Union[float, List[float], np.ndarray, pd.Series],
) -> float:
    cashflow = make_list(cashflow)
    probabilities = make_list(probabilities)
    discounters = make_list(discounters)
    return sum(
        c * probabilities[i] / (1 + discounters[i]) ** i for i, c in enumerate(cashflow)
    )


# lapse rate dependent on gender; lapse == 0 with no lapse assumption
def lapse_rate(isMale: bool, assume_lapse: bool = True) -> List[float]:
    lapse_rate = [0.0]
    if assume_lapse:
        col_ind = 0 if isMale else 1
        lapse_column = (lapse_tbl.iloc[:, col_ind] / 100).to_list()
        lapse_rate.extend(
            lapse_column[:-1] + [lapse_column[-2]] * (29 - 26) + [lapse_column[-1]]
        )
    return make_list(lapse_rate)
