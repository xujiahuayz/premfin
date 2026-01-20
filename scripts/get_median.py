import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from process_mortality_table import mortality_experience

from premiumFinance.constants import FIGURE_FOLDER
from premiumFinance.treasury_yield import yield_curve
from premiumFinance.util import cash_flow_pv

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
WORKING_LIFE_YEARS = 20
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
        # 200 * WORKING_LIFE_YEARS,
        sum(cash_flow_pv(
            cashflow=3_000 * (0.14 - 0.01),
            probabilities=1,
            discounters=yield_curve
        )[:WORKING_LIFE_YEARS]),
        # (3_800 * 0.14 - 3_000 * 0.01 - (3_800 - 3_000) * 0.14) * WORKING_LIFE_YEARS,
        # https://www.pewresearch.org/fact-tank/2020/03/25/more-than-half-of-u-s-households-have-some-investment-in-the-stock-market/ft_20-03-23_stocksimportance/
        sum(cash_flow_pv(
            cashflow=40_000 * Underdiversification_LOSS,
            probabilities=1,
            discounters=yield_curve
        )[:WORKING_LIFE_YEARS]),
        # median_stockholding * Underdiversification_LOSS * 5,
        median_value_lapsed,
    ],
    "labelname": [
        "Failure to\n refinance mortgage",
        "Overborrowing in\n credit card debt",
        "Underdiversification\n of stock market",
        "Lapsation of life insurance\n per household",
    ],
}


if __name__ == "__main__":

    y_pos = range(len(HOUSEHOLD_MISTAKES_DICT["labelname"]))
    widths = HOUSEHOLD_MISTAKES_DICT["value"]

    # Change to barh (horizontal bar)
    barlist = plt.barh(y=y_pos, width=widths, color="gray")
    barlist[-1].set_color("green")

    # Change xticks to yticks
    plt.yticks(
        y_pos,
        HOUSEHOLD_MISTAKES_DICT["labelname"],
    )
    
    # Label moves to x-axis
    plt.xlabel("USD")

    # Adjust text coordinates for horizontal layout
    for i, w in enumerate(widths):
        plt.text(
            x=w * 1.02,          # Place text slightly to the right of the bar end
            y=y_pos[i],          # Align with the y-position of the bar
            s="{:,}".format(round(w)),
            va="center",         # Vertically align to the center of the bar
            ha="left",           # Horizontally align to the left (text starts after x)
            rotation=0,
        )

    # Set x limits instead of y limits (add extra space for text)
    plt.xlim(0, max(widths) * 1.25)

    plt.tight_layout()

    plt.savefig(FIGURE_FOLDER / "householdmistakes.pdf")
    plt.show()