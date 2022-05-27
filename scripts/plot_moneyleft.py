#%% import packages
from os import path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import xlrd

from premiumFinance.fetchdata import getMarketSize
from premiumFinance.constants import (
    DATA_FOLDER,
    FIGURE_FOLDER,
)

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")

#%% calculate dollar profit

mortality_experience = pd.read_excel(untapped_profit_path)

mortality_experience["Dollar profit"].sum() / mortality_experience[
    "Amount Exposed"
].sum()

sample_representativeness = (
    getMarketSize(year=2020) / mortality_experience["Amount Exposed"].sum()
)

mortality_experience["Excess_Policy_PV_yield_curve_none0"] = mortality_experience[
    "Excess_Policy_PV_yield_curve"
]

mortality_experience["Excess_Policy_PV_yield_curve_none0"][
    mortality_experience["Excess_Policy_PV_yield_curve_none0"] < 0
] = 0

money_left_array = []
investor_coc = [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, "yield_curve"]
for i in investor_coc:
    money_left = (
        sum(
            w
            for w in mortality_experience[f"Excess_Policy_PV_{i}"]
            * mortality_experience["Amount Exposed"]
            if w > 0
        )
        * sample_representativeness
    )
    money_left_array.append(money_left)

    print(
        f"when policyholder rate equals {i}, total money left on the table: {money_left}"
    )

# https://www.federalreserve.gov/releases/z1/20120607/z1.pdf page 113
real_estate_nominal = 23523.6 / 1e3

# change from 2007-2009
real_estate_change = (23523.6 - 18874.5) / 1e3

WIDTH = 1

colors = ["blue", "green"]


#%% latest plot

heights = [
    real_estate_nominal,
    getMarketSize(year=2020) / 1e12,
    real_estate_change,
    money_left_array[-1] / 1e12,
]

x_pos = [0, WIDTH, 3 * WIDTH, 4 * WIDTH]

plt.bar(
    x=x_pos[:2],
    height=heights[:2],
    width=WIDTH,
    color=colors,
    edgecolor="k",
)


plt.bar(
    x=x_pos[2:],
    height=heights[2:],
    width=WIDTH,
    color=colors,
    edgecolor="k",
)

for i, h in enumerate(heights):
    plt.text(
        x=x_pos[i],
        y=1.02 * heights[i],
        s="{:.2f}".format(heights[i]),
        ha="center",
        va="bottom",
        rotation=0,
    )


plt.xticks(
    x_pos,
    [
        "Real estate market size",
        "Life insurance face amount",
        "Real estate value lost",
        "Life insurance value to policyholders",
    ],
    rotation=45,
)

plt.ylabel("trillion USD")
plt.ylim(0, max(heights) * 1.1)

plt.tight_layout()

plt.savefig(path.join(FIGURE_FOLDER, "moneyleft.pdf"))

#%% money left distribution
mortality_experience["money_left"] = (
    mortality_experience["Excess_Policy_PV_yield_curve_none0"]
    * mortality_experience["Amount Exposed"]
    * sample_representativeness
)

money_left_grouped = mortality_experience.groupby(["currentage", "isMale"])[
    "money_left"
].sum()


## BELOW IS DEPRECATED

#%% money left plot

plt.bar(x=0, height=real_estate_nominal)

plt.bar(x=WIDTH, height=[getMarketSize(year=2020) / 1e12])


plt.xticks(
    [0, WIDTH],
    [
        "Real estate",
        "Life insurance",
    ],
    rotation=90,
)
plt.ylabel("trillion USD")


plt.show()

plt.bar(x=0, height=real_estate_change)

plt.bar(x=WIDTH, height=money_left_array[-1] / 1e12)


plt.xticks(
    [0, WIDTH],
    [
        "Real estate value loss",
        "Life insurance money left",
    ],
    rotation=90,
)
plt.ylabel("trillion USD")

plt.show()

#%% old plot
plt.bar(
    x=0,
    height=real_estate_nominal,
    width=WIDTH,
    color="blue",
    edgecolor="k",
)

plt.bar(
    x=WIDTH,
    height=real_estate_change,
    width=WIDTH,
    color="green",
    edgecolor="k",
)


x_pos = np.arange(len(money_left_array))

plt.bar(
    x=3 * WIDTH,
    height=[getMarketSize(year=2020) / 1e12],
    width=WIDTH,
    color="blue",
    edgecolor="k",
    # tick_label=["Total Face"],
)

plt.bar(
    x=x_pos + 4 * WIDTH,
    height=np.array(money_left_array) / 1e12,
    width=WIDTH,
    color="green",
    edgecolor="k",
    # tick_label=investor_coc,
)

plt.xticks(
    [0, WIDTH, 3 * WIDTH] + (x_pos + 4 * WIDTH).tolist(),
    [
        "Real estate",
        "Value lost",
        "Life insurance",
    ]
    + investor_coc,
    rotation=90,
)
plt.ylabel("trillion USD")

# %%
