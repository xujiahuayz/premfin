#%% import packages
from os import path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import xlrd

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
#%% money left distribution subject to age and sex
# sex_age_distribution
bins = np.arange(20, 110, 10)
group_age = pd.cut(mortality_experience["currentage"], bins=bins)
df = mortality_experience.loc[:, ["isMale", "money_left"]]
df["Age_cat"] = group_age
group_age_sex = df.groupby(["isMale", "Age_cat"], as_index=False).sum()
group_age_sex["Age_cat"] = group_age_sex["Age_cat"].astype(str)

X_label = sorted(set(group_age_sex["Age_cat"]))
man_money = group_age_sex[group_age_sex["isMale"] == True]["money_left"] / 1e12
woman_money = group_age_sex[group_age_sex["isMale"] == False]["money_left"] / 1e12

plt.bar(X_label, height=man_money, width=0.7, color="blue", edgecolor="k", label="Man")
plt.bar(
    X_label,
    height=woman_money,
    bottom=man_money,
    width=0.7,
    color="pink",
    edgecolor="k",
    label="Woman",
)
for x, y in enumerate(zip(man_money, woman_money)):
    plt.text(x, y[0] / 2, "%s" % round(y[0], 2), ha="center", va="bottom", fontsize=8)
    plt.text(
        x, max(y[0] / 2+0.03,y[1] / 2 + y[0]), "%s" % round(y[1], 2), ha="center", va="bottom", fontsize=8
    )
    plt.text(
        x,
        max(y[1] + y[0],y[0] / 2+0.2),
        "%s" % round(y[1] + y[0],2),
        ha="center",
        va="bottom",
        fontsize=8,
    )
plt.xticks(rotation=45)
plt.ylabel("Trillion USD")
plt.xlabel("Age")
plt.legend()
plt.savefig(path.join(FIGURE_FOLDER, "moneyleft_sex_age_distribution.pdf"))
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
