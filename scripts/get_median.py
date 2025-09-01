import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from process_mortality_table import mortality_experience

from premiumFinance.constants import FIGURE_FOLDER

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

    plt.savefig(FIGURE_FOLDER / "householdmistakes.pdf")
    plt.show()
