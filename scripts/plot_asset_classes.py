# https://www.sifma.org/resources/research/us-corporate-bonds-statistics/
# YTD statistics include:

# Issuance (as of August) $1,342.7 billion, +31.3% Y/Y
# Trading (as of August) $48.7 billion ADV, +19.9% Y/Y
# Outstanding (as of 2Q24) $11.0 trillion, +3.4% Y/Y

# US 2023
# Equity market cap
# 48,979.3977 $B

# US Holdings of Equities - Market Value
# household holding
# 31,583.8 $B


# US municipal bonds 2023
# outstanding
# 4,056.922 $B

# US corporate bonds 2023
# outstanding
# 10,730.194 $B


# https://www.federalreserve.gov/apps/FOF/Guide/L217.pdf

from premiumFinance.fetchdata import get_market_size
from premiumFinance.constants import FIGURE_FOLDER
import matplotlib.pyplot as plt


life_insurance_market = get_market_size(year=2020) / 1e12


#  bar chart with life insurance market size, equity market cap, corporate bond outstanding, and municipal bonds outstanding
# with label under each bar

heights = [
    life_insurance_market,
    48.9793977,
    10.730194,
    4.056922,
]

# x_pos = [0, 1, 2, 3]

plt.bar(
    x=range(len(heights)),
    height=heights,
    color="skyblue",
    edgecolor="k",
)

plt.xticks(
    range(len(heights)),
    [
        "Life insurance market size",
        "Equity market cap",
        "Corporate bond outstanding",
        "Municipal bond outstanding",
    ],
    rotation=45,
)

for i, h in enumerate(heights):
    plt.text(
        x=i,
        y=1.005 * heights[i],
        s="{:.2f}".format(heights[i]),
        ha="center",
        va="bottom",
        rotation=0,
    )

# y-axis label
plt.ylabel("trillions USD")

# save to pdf
plt.savefig(FIGURE_FOLDER / "asset_classes.pdf", bbox_inches="tight")
