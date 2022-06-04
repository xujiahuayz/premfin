from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER
from premiumFinance.fetchdata import getMarketSize
from premiumFinance.util import lapse_rate

import pandas as pd
from os import path
import matplotlib.pyplot as plt
import numpy as np

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
    # %%
    # Breakdown lapsed economic value
    plt.show()
    bins = np.arange(20, 110, 10)
    group_age = pd.cut(mortality_experience["currentage"], bins=bins)
    df = mortality_experience.loc[:, ["isMale", "lapsed_economic_value"]]
    df["Age_cat"] = group_age
    group_age_sex = df.groupby(["isMale", "Age_cat"], as_index=False).sum()
    group_age_sex["Age_cat"] = group_age_sex["Age_cat"].astype(str)
    # %%
    X_label = sorted(set(group_age_sex["Age_cat"]))
    man_money = (
        group_age_sex[group_age_sex["isMale"] == True]["lapsed_economic_value"]
        / 1e9
        * sample_representativeness
    )
    woman_money = (
        group_age_sex[group_age_sex["isMale"] == False]["lapsed_economic_value"]
        / 1e9
        * sample_representativeness
    )

    plt.bar(X_label, height=man_money, width=0.7, color="royalblue", label="Man")
    plt.bar(
        X_label,
        height=woman_money,
        bottom=man_money,
        width=0.7,
        color="pink",
        label="Woman",
    )
    for x, y in enumerate(zip(man_money, woman_money)):
        plt.text(
            x,
            max(y[0] / 2, 4),
            "%s" % round(y[0], 2),
            ha="center",
            va="bottom",
            fontsize=8,
        )
        plt.text(
            x,
            max(y[1] / 2 + y[0], y[0] / 2 + 8),
            "%s" % round(y[1], 2),
            ha="center",
            va="bottom",
            fontsize=8,
        )
        plt.text(
            x,
            max(y[1] + y[0], y[1] / 2 + y[0] + 10, y[1] / 2 + y[0] + 10),
            "%s" % round(y[1] + y[0], 2),
            ha="center",
            va="bottom",
            fontsize=8,
        )
    plt.xticks(rotation=45)
    plt.ylabel("billion USD")
    plt.xlabel("age")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path.join(FIGURE_FOLDER, "lap_bd.pdf"))
    plt.show()
