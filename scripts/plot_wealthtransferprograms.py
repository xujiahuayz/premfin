import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from premiumFinance.constants import FIGURE_FOLDER
from scripts.process_mortality_table import mortality_experience
from scripts.sample_represent import sample_representativeness

lapsed_value_all = mortality_experience["lapsed_economic_value"].sum()

WEALTHTRANSFER_PROGRAMS_DICT = {
    "value": [
        99.8,
        # 57.6,
        60,
        33.29,
        # 16.5,
        lapsed_value_all / 1e9,
    ],
    "labelname": [
        "Supplemental Nutrition\n Assistance Program",
        # "Supplemental Security Income",
        "Medicaid prescription\n drug spending",
        "Unemployment Insurance\nexpenditures",
        # "Temporary Assistance\nfor Needy Families",
        "Lapsed life insurance\n economic value",
    ],
}

# %%
if __name__ == "__main__":
    y_pos = range(len(WEALTHTRANSFER_PROGRAMS_DICT["labelname"]))
    widths = WEALTHTRANSFER_PROGRAMS_DICT["value"]

    # Change to barh (horizontal bar)
    barlist = plt.barh(y=y_pos, width=widths, color="gray")
    barlist[-1].set_color("green")

    # Change xticks to yticks
    plt.yticks(
        y_pos,
        WEALTHTRANSFER_PROGRAMS_DICT["labelname"],
    )
    
    # Label moves to x-axis
    plt.xlabel("billion USD")

    # Adjust text coordinates for horizontal layout
    for i, w in enumerate(widths):
        plt.text(
            x=w * 1.01,          # Place text slightly to the right of the bar end
            y=y_pos[i],          # Align with the y-position of the bar
            s="{:.2f}".format(w),
            va="center",         # Vertically align to the center of the bar
            ha="left",           # Horizontally align to the left (text starts after x)
            rotation=0,
        )

    # Set x limits instead of y limits (add extra space for text)
    plt.xlim(0, max(widths) * 1.15)

    plt.tight_layout()

    plt.savefig(FIGURE_FOLDER / "wealthtransferprograms.pdf")