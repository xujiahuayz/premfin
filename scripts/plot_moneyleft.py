# %% import packages
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import brewer2mpl


from premiumFinance.fetchdata import get_market_size
from premiumFinance.constants import (
    FIGURE_FOLDER,
    MORTALITY_TABLE_CLEANED_PATH,
)


# %% calculate dollar profit
mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)
sample_representativeness = (
    get_market_size(year=2020) / mortality_experience["Amount Exposed"].sum()
)


def get_money_left(
    current_vbt: str = "VBT15",
    lapse_assumption: bool = True,
    current_mort: float = 1,
    premium_hike: float = 0,
) -> float:
    """
    get money left value in different scenarios
    """
    return (
        sum(
            w
            for w in mortality_experience[
                f"Excess_Policy_PV_{current_vbt}_lapse{lapse_assumption}_mort{current_mort}_coihike_{premium_hike}"
            ]
            * mortality_experience["Amount Exposed"]
        )
        * sample_representativeness
    )


money_left_15_T = get_money_left(current_vbt="VBT15", lapse_assumption=True)

if __name__ == "__main__":
    money_left_01_T = get_money_left(current_vbt="VBT01", lapse_assumption=True)
    money_left_15_F = get_money_left(current_vbt="VBT15", lapse_assumption=False)

    # https://www.federalreserve.gov/releases/z1/20120607/z1.pdf page 113
    real_estate_nominal = 23523.6 / 1e3

    # change from 2007-2009
    real_estate_change = (23523.6 - 18874.5) / 1e3

    WIDTH = 1
    # %%
    bmap_5 = brewer2mpl.get_map("greens", "sequential", 5)
    bmap_3 = brewer2mpl.get_map("dark2", "qualitative", 3)
    colors = bmap_3.mpl_colors
    colors_5 = bmap_5.mpl_colors
    colors.extend(colors_5[::-1])
    # %%

    # %% latest plot
    heights = [
        real_estate_nominal,
        get_market_size(year=2020) / 1e12,
        real_estate_change,
        money_left_01_T / 1e12,
        money_left_15_T / 1e12,
        money_left_15_F / 1e12,
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
    plt.savefig(FIGURE_FOLDER / "moneyleft.pdf")
    plt.show()


# #%% money left distribution subject to age and sex
# # sex_age_distribution
# mortality_experience["money_left"] = (
#     mortality_experience[f"Excess_Policy_PV_VBT15_lapseTrue_mort1"]
#     * mortality_experience["Amount Exposed"]
# )
# bins = np.arange(20, 110, 10)
# df = mortality_experience.loc[:, ["isMale", "money_left"]]
# df["Age_cat"] = pd.cut(mortality_experience["currentage"], bins=bins).astype(str)
# group_age_sex = df.groupby(["isMale", "Age_cat"], as_index=False).sum()

# X_label = sorted(set(group_age_sex["Age_cat"]))
# man_money = group_age_sex[group_age_sex["isMale"] == True]["money_left"] / 1e12
# woman_money = group_age_sex[group_age_sex["isMale"] == False]["money_left"] / 1e12

# plt.bar(X_label, height=man_money, width=0.7, color="royalblue", label="male")
# plt.bar(
#     X_label,
#     height=woman_money,
#     bottom=man_money,
#     width=0.7,
#     color="pink",
#     label="female",
# )
# for x, y in enumerate(zip(man_money, woman_money)):
#     plt.text(x, y[0] / 2, "%s" % round(y[0], 2), ha="center", va="bottom", fontsize=8)
#     plt.text(
#         x,
#         max(y[0] / 2 + 0.03, y[1] / 2 + y[0]),
#         "%s" % round(y[1], 2),
#         ha="center",
#         va="bottom",
#         fontsize=8,
#     )
#     plt.text(
#         x,
#         max(y[1] + y[0], y[0] / 2 + 0.2),
#         "%s" % round(y[1] + y[0], 2),
#         ha="center",
#         va="bottom",
#         fontsize=8,
#     )
# plt.xticks(rotation=45)
# plt.ylabel("trillion USD")
# plt.xlabel("age")
# plt.legend()
# plt.tight_layout()
# plt.savefig(path.join(FIGURE_FOLDER, "moneyleft_sex_age_distribution.pdf"))
# plt.show()
# #%%

# mortality_experience["Excess_Policy_PV_yield_curve_none0"] = mortality_experience[
#     "Excess_Policy_PV_yield_curve"
# ]
# mortality_experience["money_left"] = (
#     mortality_experience["Excess_Policy_PV_yield_curve_none0"]
#     * mortality_experience["Amount Exposed"]
#     * sample_representativeness
# )
# mortality_experience["Face_Value"] = (
#     mortality_experience["Amount Exposed"] / mortality_experience["Policies Exposed"]
# )
# df = mortality_experience.loc[
#     :,
#     [
#         "Amount Exposed",
#         "Policies Exposed",
#         "Excess_Policy_PV_yield_curve_none0",
#         "money_left",
#         "Face_Value",
#     ],
# ]
# bins = np.array([999, 10000, 100000, 500000, 1000000, 5000000])
# df["cat"] = pd.cut(df["Face_Value"], bins).astype(str)
# X_label = sorted(set(df["cat"]), key=lambda x: int(x.split(",")[1][1:-2]))
# sum_dict = dict()
# for i in range(len(X_label)):
#     sum_dict[X_label[i]] = df[df["cat"] == X_label[i]]["money_left"].sum()

# #%%
# df["avr"] = df.apply(
#     lambda row: row["Excess_Policy_PV_yield_curve_none0"]
#     * row["money_left"]
#     / sum_dict[row["cat"]],
#     axis=1,
# )
# avr = list(df["avr"].groupby(df["cat"]).sum().iteritems())
# avr = sorted(avr, key=lambda x: int(x[0].split(",")[1][1:-2]))
# for i in range(len(avr)):
#     avr[i] = avr[i][1]
# #%%
# plt.bar(X_label, height=avr, width=0.7, color="royalblue", label="average value")
# for x, y in enumerate(avr):
#     plt.text(x, y, "%s" % round(y, 2), ha="center", va="bottom", fontsize=8)
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.savefig(path.join(FIGURE_FOLDER, "moneyleft_pv_bd.pdf"))
# plt.show()
