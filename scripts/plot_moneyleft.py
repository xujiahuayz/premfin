#%% import packages
from os import path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import brewer2mpl

# import xlrd

from premiumFinance.fetchdata import getMarketSize
from premiumFinance.constants import (
    DATA_FOLDER,
    FIGURE_FOLDER,
)

untapped_profit_path_15_T = path.join(DATA_FOLDER, "untappedprofit.xlsx")
untapped_profit_path_01_T = path.join(DATA_FOLDER, "untappedprofit_cnt.xlsx")
untapped_profit_path_15_F = path.join(DATA_FOLDER, "untappedprofit_cnt_false.xlsx")
untapped_profit_path_15_T_mort03 = path.join(
    DATA_FOLDER, "untappedprofit_cnt_15_T_mort03.xlsx"
)
#%% import packages
untapped_profit_path_15_T_mort5 = path.join(
    DATA_FOLDER, "untappedprofit_cnt_15_T_mort5.xlsx"
)
untapped_profit_path_15_T_mort3 = path.join(
    DATA_FOLDER, "untappedprofit_cnt_15_T_mort3.xlsx"
)
untapped_profit_path_15_T_mort03 = path.join(
    DATA_FOLDER, "untappedprofit_cnt_15_T_mort03.xlsx"
)
untapped_profit_path_15_T_mort05 = path.join(
    DATA_FOLDER, "untappedprofit_cnt_15_T_mort05.xlsx"
)
#%% calculate dollar profit
def get_money_left_arr(untapped_profit_path):
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

    money_left_array = []
    investor_coc = [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, "yield_curve"]
    for i in investor_coc:
        money_left = (
            sum(
                w
                for w in mortality_experience[f"Excess_Policy_PV_{i}"]
                * mortality_experience["Amount Exposed"]
            )
            * sample_representativeness
        )
        money_left_array.append(money_left)

        print(
            f"when policyholder rate equals {i}, total money left on the table: {money_left}"
        )
    return money_left_array


# https://www.federalreserve.gov/releases/z1/20120607/z1.pdf page 113
real_estate_nominal = 23523.6 / 1e3

# change from 2007-2009
real_estate_change = (23523.6 - 18874.5) / 1e3

WIDTH = 1
#%%
bmap_5 = brewer2mpl.get_map("greens", "sequential", 5)
bmap_3 = brewer2mpl.get_map("dark2", "qualitative", 3)
colors = bmap_3.mpl_colors
colors_5 = bmap_5.mpl_colors
colors.extend(colors_5[::-1])
#%%
money_left_15_T = get_money_left_arr(untapped_profit_path_15_T)
money_left_01_T = get_money_left_arr(untapped_profit_path_01_T)
money_left_15_F = get_money_left_arr(untapped_profit_path_15_F)
# money_left_15_T_mort5 = get_money_left_arr(untapped_profit_path_15_T_mort5)
# money_left_15_T_mort3 = get_money_left_arr(untapped_profit_path_15_T_mort3)
# money_left_15_T_mort03 = get_money_left_arr(untapped_profit_path_15_T_mort03)
money_left_15_T_mort05 = get_money_left_arr(untapped_profit_path_15_T_mort05)
#%%
#%% latest plot
heights = [
    real_estate_nominal,
    getMarketSize(year=2020) / 1e12,
    real_estate_change,
    money_left_01_T[-1] / 1e12,
    money_left_15_T[-1] / 1e12,
    money_left_15_F[-1] / 1e12,
]

x_pos = [0, WIDTH, 3 * WIDTH, 4 * WIDTH]

plt.bar(
    x=x_pos[:3],
    height=heights[:3],
    width=WIDTH,
    color=colors[:3],
    edgecolor="k",
)
for i in range(3, len(heights)):
    plt.bar(
        x=x_pos[3],
        height=heights[i],
        width=WIDTH,
        color=colors[i],
        edgecolor="k",
    )

for i, h in enumerate(heights[0:3]):
    plt.text(
        x=x_pos[i],
        y=1.02 * heights[i],
        s="{:.2f}".format(heights[i]),
        ha="center",
        va="bottom",
        rotation=0,
    )
for i, h in enumerate(heights[3:]):
    plt.text(
        x=x_pos[3],
        y=heights[i + 3],
        s="{:.2f}".format(heights[i + 3]),
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
custom_lines = [
    Line2D([0], [0], color=colors[3], lw=4),
    Line2D([0], [0], color=colors[4], lw=4),
    Line2D([0], [0], color=colors[5], lw=4),
]
plt.legend(custom_lines, ["VBT01 T 1", "VBT15 T 1", "VBT15 F 1"])
plt.ylim(0, sum(heights[3:]) * 1.3)
plt.tight_layout()
plt.savefig(path.join(FIGURE_FOLDER, "moneyleft.pdf"))
plt.show()

#%% money left distribution
mortality_experience = pd.read_excel(untapped_profit_path_15_T)
sample_representativeness = (
    getMarketSize(year=2020) / mortality_experience["Amount Exposed"].sum()
)
mortality_experience["Excess_Policy_PV_yield_curve_none0"] = mortality_experience[
    "Excess_Policy_PV_yield_curve"
]

mortality_experience["money_left"] = (
    mortality_experience["Excess_Policy_PV_yield_curve_none0"]
    * mortality_experience["Amount Exposed"]
    * sample_representativeness
)


#%% money left distribution subject to age and sex
# sex_age_distribution
bins = np.arange(20, 110, 10)
df = mortality_experience.loc[:, ["isMale", "money_left"]]
df["Age_cat"] = pd.cut(mortality_experience["currentage"], bins=bins).astype(str)
group_age_sex = df.groupby(["isMale", "Age_cat"], as_index=False).sum()

X_label = sorted(set(group_age_sex["Age_cat"]))
man_money = group_age_sex[group_age_sex["isMale"] == True]["money_left"] / 1e12
woman_money = group_age_sex[group_age_sex["isMale"] == False]["money_left"] / 1e12

plt.bar(X_label, height=man_money, width=0.7, color="royalblue", label="male")
plt.bar(
    X_label,
    height=woman_money,
    bottom=man_money,
    width=0.7,
    color="pink",
    label="female",
)
for x, y in enumerate(zip(man_money, woman_money)):
    plt.text(x, y[0] / 2, "%s" % round(y[0], 2), ha="center", va="bottom", fontsize=8)
    plt.text(
        x,
        max(y[0] / 2 + 0.03, y[1] / 2 + y[0]),
        "%s" % round(y[1], 2),
        ha="center",
        va="bottom",
        fontsize=8,
    )
    plt.text(
        x,
        max(y[1] + y[0], y[0] / 2 + 0.2),
        "%s" % round(y[1] + y[0], 2),
        ha="center",
        va="bottom",
        fontsize=8,
    )
plt.xticks(rotation=45)
plt.ylabel("trillion USD")
plt.xlabel("age")
plt.legend()
plt.tight_layout()
plt.savefig(path.join(FIGURE_FOLDER, "moneyleft_sex_age_distribution.pdf"))
plt.show()
#%%
mortality_experience = pd.read_excel(untapped_profit_path_15_T)
sample_representativeness = (
    getMarketSize(year=2020) / mortality_experience["Amount Exposed"].sum()
)
mortality_experience["Excess_Policy_PV_yield_curve_none0"] = mortality_experience[
    "Excess_Policy_PV_yield_curve"
]
mortality_experience["money_left"] = (
    mortality_experience["Excess_Policy_PV_yield_curve_none0"]
    * mortality_experience["Amount Exposed"]
    * sample_representativeness
)
mortality_experience["Face_Value"] = (
    mortality_experience["Amount Exposed"] / mortality_experience["Policies Exposed"]
)
df = mortality_experience.loc[
    :,
    [
        "Amount Exposed",
        "Policies Exposed",
        "Excess_Policy_PV_yield_curve_none0",
        "money_left",
        "Face_Value",
    ],
]
bins = np.array([999, 10000, 100000, 500000, 1000000, 5000000])
df["cat"] = pd.cut(df["Face_Value"], bins).astype(str)
X_label = sorted(set(df["cat"]), key=lambda x: int(x.split(",")[1][1:-2]))
sum_dict = dict()
for i in range(len(X_label)):
    sum_dict[X_label[i]] = df[df["cat"] == X_label[i]]["money_left"].sum()

#%%
df["avr"] = df.apply(
    lambda row: row["Excess_Policy_PV_yield_curve_none0"]
    * row["money_left"]
    / sum_dict[row["cat"]],
    axis=1,
)
avr = list(df["avr"].groupby(df["cat"]).sum().iteritems())
avr = sorted(avr, key=lambda x: int(x[0].split(",")[1][1:-2]))
for i in range(len(avr)):
    avr[i] = avr[i][1]
#%%
plt.bar(X_label, height=avr, width=0.7, color="royalblue", label="average value")
for x, y in enumerate(avr):
    plt.text(x, y, "%s" % round(y, 2), ha="center", va="bottom", fontsize=8)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(path.join(FIGURE_FOLDER, "moneyleft_pv_bd.pdf"))
plt.show()
#%%
# ## BELOW IS DEPRECATED

# #%% money left plot

# plt.bar(x=0, height=real_estate_nominal)

# plt.bar(x=WIDTH, height=[getMarketSize(year=2020) / 1e12])


# plt.xticks(
#     [0, WIDTH],
#     [
#         "Real estate",
#         "Life insurance",
#     ],
#     rotation=90,
# )
# plt.ylabel("trillion USD")


# plt.show()

# plt.bar(x=0, height=real_estate_change)

# plt.bar(x=WIDTH, height=money_left_array[-1] / 1e12)


# plt.xticks(
#     [0, WIDTH],
#     [
#         "Real estate value loss",
#         "Life insurance money left",
#     ],
#     rotation=90,
# )
# plt.ylabel("trillion USD")

# #%% old plot
# plt.bar(
#     x=0,
#     height=real_estate_nominal,
#     width=WIDTH,
#     color="blue",
#     edgecolor="k",
# )

# plt.bar(
#     x=WIDTH,
#     height=real_estate_change,
#     width=WIDTH,
#     color="green",
#     edgecolor="k",
# )


# x_pos = np.arange(len(money_left_array))

# plt.bar(
#     x=3 * WIDTH,
#     height=[getMarketSize(year=2020) / 1e12],
#     width=WIDTH,
#     color="blue",
#     edgecolor="k",
#     # tick_label=["Total Face"],
# )

# plt.bar(
#     x=x_pos + 4 * WIDTH,
#     height=np.array(money_left_array) / 1e12,
#     width=WIDTH,
#     color="green",
#     edgecolor="k",
#     # tick_label=investor_coc,
# )

# plt.xticks(
#     [0, WIDTH, 3 * WIDTH] + (x_pos + 4 * WIDTH).tolist(),
#     [
#         "Real estate",
#         "Value lost",
#         "Life insurance",
#     ]
#     + investor_coc,
#     rotation=90,
# )
# plt.ylabel("trillion USD")

# # %%

# %%
