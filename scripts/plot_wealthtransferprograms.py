from premiumFinance.constants import FIGURE_FOLDER
from premiumFinance.fetchdata import lapse_tbl

import pandas as pd
from os import path
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt


#
WEALTHTRANSFER_PROGRAMS_DICT = {
    "value": [
        84,
        799.4,
        613.5,
        143,
    ],
    "labelname": [
        "Food stamp",
        "Medicare",
        "Medicaid",
        "Life insurance premium",
    ],
}


if __name__ == "__main__":

    x_pos = range(len(WEALTHTRANSFER_PROGRAMS_DICT["labelname"]))
    barlist = plt.bar(x=x_pos, height=WEALTHTRANSFER_PROGRAMS_DICT["value"])
    barlist[-1].set_color("green")

    plt.xticks(
        x_pos,
        WEALTHTRANSFER_PROGRAMS_DICT["labelname"],
        rotation=45,
    )
    plt.ylabel("billion USD")

    plt.tight_layout()

    plt.savefig(path.join(FIGURE_FOLDER, "wealthtransferprograms.pdf"))
