from typing import Union
import numpy as np
import pandas as pd
from typing import Optional

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
