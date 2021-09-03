from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER
from premiumFinance.fetchdata import getMarketSize
from premiumFinance.util import lapse_rate

import pandas as pd
from os import path
import matplotlib.pyplot as plt


untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")

mortality_experience = pd.read_excel(untapped_profit_path)

mortality_experience["lapse_rate"] = mortality_experience.apply(
    lambda row: lapse_rate(isMale=row["isMale"])[row["currentage"] - row["issueage"]],
    axis=1,
)

mortality_experience["lapsed_economic_value"] = (
    mortality_experience["lapse_rate"]
    * mortality_experience["Excess_Policy_PV_yield_curve"]
    * mortality_experience["Amount Exposed"]
)

sample_representativeness = (
    getMarketSize(year=2020) / mortality_experience["Amount Exposed"].sum()
)

lapsed_value_all = (
    mortality_experience["lapsed_economic_value"].sum() * sample_representativeness
)


# lapsed_value_positive_only = (
#     sum(w for w in mortality_experience["lapsed_economic_value"] if w > 0)
#     * sample_representativeness
# )

WEALTHTRANSFER_PROGRAMS_DICT = {
    "value": [
        84,
        799.4,
        613.5,
        lapsed_value_all / 1e9,
    ],
    "labelname": [
        "Food stamp",
        "Medicare",
        "Medicaid",
        "Lapsed life insurance \n economic value",
    ],
}


if __name__ == "__main__":

    x_pos = range(len(WEALTHTRANSFER_PROGRAMS_DICT["labelname"]))
    heights = WEALTHTRANSFER_PROGRAMS_DICT["value"]

    barlist = plt.bar(x=x_pos, height=heights)
    barlist[-1].set_color("green")

    plt.xticks(
        x_pos,
        WEALTHTRANSFER_PROGRAMS_DICT["labelname"],
        rotation=45,
    )
    plt.ylabel("billion USD")

    for i, h in enumerate(heights):
        plt.text(
            x=x_pos[i],
            y=1.02 * heights[i],
            s="{:.2f}".format(heights[i]),
            ha="center",
            va="bottom",
            rotation=0,
        )

    plt.ylim(0, max(heights) * 1.1)

    plt.tight_layout()

    plt.savefig(path.join(FIGURE_FOLDER, "wealthtransferprograms.pdf"))
