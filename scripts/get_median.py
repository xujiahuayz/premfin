# COL_NAMES = ["Gender", "Smoker Status",	"Issue Age", "Attained Age", "Amount Exposed", 	Policies Exposed 	Death Claim Amount 	Sum of Number of Deaths
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER
#from premiumFinance.fetchdata import getMarketSize
from premiumFinance.util import lapse_rate

import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot as plt
from itertools import product

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")

mortality_experience = pd.read_excel(untapped_profit_path)

mortality_experience["lapse_rate"] = mortality_experience.apply(
    lambda row: lapse_rate(isMale=row["isMale"])[row["currentage"] - row["issueage"]],
    axis=1,
)


mortality_experience["number_lapsed_policies"] = (
    mortality_experience["lapse_rate"] * mortality_experience["Policies Exposed"]
)

mortality_experience["average_lapsed_amount"] = (
    mortality_experience["Excess_Policy_PV_yield_curve"]
    * mortality_experience["Amount Exposed"]
    / mortality_experience["Policies Exposed"]
)

mortality_experience_sorted = mortality_experience.sort_values(
    by=["average_lapsed_amount"], ignore_index=True
)

mortality_experience_sorted["number_policies_cumsum"] = mortality_experience_sorted[
    "number_lapsed_policies"
].cumsum()

median_value_lapsed = mortality_experience_sorted.loc[
    (
        mortality_experience_sorted["number_policies_cumsum"]
        > mortality_experience_sorted["number_policies_cumsum"].iloc[-1] / 2
    ).values,
    "average_lapsed_amount",
].iat[0]
# 46190.03282643981
WORKING_LIFE_YEARS = 25
Underdiversification_LOSS = 0.0204

age_freq = mortality_experience.groupby("currentage")["Policies Exposed"].sum()
age_distribution = age_freq / age_freq.sum()

stock_holding = pd.DataFrame(
    {
        "age": ["<35", "35_44", "45_54", "55_64", ">65"],
        "distribution": [
            age_distribution.loc[age_distribution.index < 35].sum(),
            age_distribution.loc[
                np.bitwise_and(
                    35 <= age_distribution.index, age_distribution.index <= 44
                )
            ].sum(),
            age_distribution.loc[
                np.bitwise_and(
                    45 <= age_distribution.index, age_distribution.index <= 54
                )
            ].sum(),
            age_distribution.loc[
                np.bitwise_and(
                    55 <= age_distribution.index, age_distribution.index <= 64
                )
            ].sum(),
            age_distribution.loc[age_distribution.index > 65].sum(),
        ],
        "stockholding": [7_700, 22_000, 51_000, 80_000, 100_000],
    }
).sort_values("stockholding")

stock_holding["age_dist_cumsum"] = stock_holding["distribution"].cumsum()

median_stockholding = stock_holding.loc[stock_holding["age_dist_cumsum"] > 0.5][
    "stockholding"
].iat[0]

HOUSEHOLD_MISTAKES_DICT = {
    "value": [
        11_500,
        (3_800 * 0.14 - 3_000 * 0.01 - (3_800 - 3_000) * 0.14) * WORKING_LIFE_YEARS,
        # https://www.pewresearch.org/fact-tank/2020/03/25/more-than-half-of-u-s-households-have-some-investment-in-the-stock-market/ft_20-03-23_stocksimportance/
        40_000 * Underdiversification_LOSS * WORKING_LIFE_YEARS,
        # median_stockholding * Underdiversification_LOSS * 5,
        median_value_lapsed,
    ],
    "labelname": [
        "Failure to refinance mortgage",
        "Unnecessary credit card debt",
        "Underdiversification",
        "Lapsation of life insurance",
    ],
}


def getMedian_lapsed_distr(og_mortality_experience: pd.DataFrame) -> pd.DataFrame:
    median_lapsed_distr = pd.DataFrame(
        columns=("isMale", "Age_cat", "lapsed_median"), index=None
    )
    age = np.arange(20, 100, 10)
    gender = [False, True]
    conditions = list(product(gender, age))

    for con in conditions:
        cur_mortality_experience = og_mortality_experience
        cur_mortality_experience = cur_mortality_experience[
            cur_mortality_experience.apply(
                lambda x: con[1] < x["issueage"] <= con[1] + 10
                and x["isMale"] == con[0],
                axis=1,
            )
        ]
        cur_mortality_experience_sorted = cur_mortality_experience.sort_values(
            by=["average_lapsed_amount"], ignore_index=True
        )
        cur_mortality_experience_sorted[
            "number_policies_cumsum"
        ] = cur_mortality_experience_sorted["number_lapsed_policies"].cumsum()

        cur_median_value_lapsed = cur_mortality_experience_sorted.loc[
            (
                cur_mortality_experience_sorted["number_policies_cumsum"]
                > cur_mortality_experience_sorted["number_policies_cumsum"].iloc[-1] / 2
            ).values,
            "average_lapsed_amount",
        ].iat[0]

        row = {
            "isMale": con[0],
            "Age_cat": (str(con[1]) + "-" + str(con[1] + 10)),
            "lapsed_median": cur_median_value_lapsed,
        }
        median_lapsed_distr = median_lapsed_distr.append(row, ignore_index=True)
    return median_lapsed_distr


if __name__ == "__main__":

    x_pos = range(len(HOUSEHOLD_MISTAKES_DICT["labelname"]))
    heights = HOUSEHOLD_MISTAKES_DICT["value"]

    barlist = plt.bar(x=x_pos, height=heights)
    barlist[-1].set_color("green")

    plt.xticks(
        x_pos,
        HOUSEHOLD_MISTAKES_DICT["labelname"],
        rotation=45,
    )
    plt.ylabel("USD")

    for i, h in enumerate(heights):
        plt.text(
            x=x_pos[i],
            y=1.02 * heights[i],
            s="{:,}".format(round(heights[i])),
            ha="center",
            va="bottom",
            rotation=0,
        )

    plt.ylim(0, max(heights) * 1.1)

    plt.tight_layout()

    plt.savefig(path.join(FIGURE_FOLDER, "householdmistakes.pdf"))
    plt.show()
    # Plot gender and age distribution
    group_age_sex = getMedian_lapsed_distr(mortality_experience)
    X_label = sorted(set(group_age_sex["Age_cat"]))
    man_money = group_age_sex[group_age_sex["isMale"] == True]["lapsed_median"]
    woman_money = group_age_sex[group_age_sex["isMale"] == False]["lapsed_median"]
    x_pos = np.arange(len(X_label))
    WIDTH = 0.3
    plt.bar(
        x_pos - WIDTH / 2,
        height=man_money,
        width=WIDTH,
        color="blue",
        edgecolor="k",
        label="Man",
    )
    plt.bar(
        x_pos + WIDTH / 2,
        height=woman_money,
        width=WIDTH,
        color="pink",
        edgecolor="k",
        label="Woman",
    )
    for x, y in enumerate(zip(man_money, woman_money)):
        plt.text(
            x,
            y[0],
            s="{:,}".format(round(y[0])),
            ha="center",
            va="bottom",
            fontsize=8,
            color="blue",
        )
        plt.text(
            x + WIDTH + 0.03,
            y[1],
            s="{:,}".format(round(y[1])),
            ha="center",
            va="bottom",
            fontsize=8,
            color="red",
        )
    plt.xticks(x_pos, X_label, rotation=45)
    plt.ylabel("USD")
    plt.xlabel("Age")
    plt.legend()
    plt.savefig(path.join(FIGURE_FOLDER, "householdmistakes_distri.pdf"))
    plt.show()
