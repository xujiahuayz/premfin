from typing import Union
import numpy as np
import pandas as pd
from premiumFinance.fetchdata import lapse_tbl


def median_(list_tuples: list[tuple[float, float]]) -> float:
    """
    get median from a list of tuples (value, frequency)
    """
    val, freq = np.array(list_tuples).T
    ord = np.argsort(val)
    cdf = np.cumsum(freq[ord])
    return val[ord][np.searchsorted(cdf, cdf[-1] // 2)]

LIST_LEN = 150
# make a list with length 150
def make_list(x, to_length: int = LIST_LEN) -> list[float]:
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
    cashflow: Union[float, list[float], np.ndarray, pd.Series],
    probabilities: Union[float, list[float], np.ndarray, pd.Series],
    discounters: Union[float, list[float], np.ndarray, pd.Series],
) -> float:
    cashflow = make_list(cashflow)
    probabilities = make_list(probabilities)
    discounters = make_list(discounters)
    return sum(
        c * probabilities[i] / (1 + discounters[i]) ** i for i, c in enumerate(cashflow)
    )


# lapse rate dependent on gender; lapse == 0 with no lapse assumption
def lapse_rate(isMale: bool, assume_lapse: bool = True) -> list[float]:
    lapse_rate = [0.0]
    if assume_lapse:
        col_ind = 0 if isMale else 1
        lapse_column = (lapse_tbl.iloc[:, col_ind] / 100).to_list()
        lapse_rate.extend(
            lapse_column[:-1] + [lapse_column[-2]] * (29 - 26) + [lapse_column[-1]]
        )
    return make_list(lapse_rate)

