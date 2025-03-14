# read irr_results.pickle

import pickle

from matplotlib import pyplot as plt
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER
import matplotlib.lines as mlines

with open(DATA_FOLDER / "irr_results_lapse.pickle", "rb") as f:
    results = pickle.load(f)


line_types = {0: "-", 0.5: "--", 1: ":"}
colors = {(0, 100): "blue", (0, 30): "green", (50, 100): "red"}


plt.rcParams.update({"font.size": 18})

plt.figure(figsize=(8, 6))

lapse_handle = [
    mlines.Line2D(
        [],
        [],
        color="gray",
        linestyle=line_style,
        label=premium_markup,
    )
    for premium_markup, line_style in line_types.items()
]
tp_factor_handle = [
    mlines.Line2D(
        [],
        [],
        color=color,
        label=le_range,
    )
    for le_range, color in colors.items()
]


for lapse_multiplier, line_style in line_types.items():
    for mort_mult in [1]:
        # plot tp_factor (x) vs irr (y), each range as a line plot
        # plt.figure(figsize=(10, 6))
        for ranges, color in colors.items():
            x = []
            y = []

            for result in results:
                if (
                    result["lapse_multiplier"] == lapse_multiplier
                    and result["mort_mult"] == mort_mult
                    and result["ranges"] == ranges
                ):
                    x.append(result["tp_factor"])
                    y.append(result["irr"])

            plt.plot(
                x,
                y,
                label=f"LE range: {ranges}",
                color=color,
                linestyle=line_style,
            )
            # print(ranges)
            # print(y)
        # horizontal line at 0
plt.ylim(0, 0.139)
plt.xlabel("Price factor $\kappa$")
plt.ylabel("IRR")
# plt.legend()


first_legend = plt.legend(
    handles=lapse_handle,
    frameon=False,
    loc="lower left",
    # bbox_to_anchor=(1, 1),
    handlelength=0.8,
    title="lapse multiplier",
)

plt.gca().add_artist(first_legend)
plt.legend(
    handles=tp_factor_handle,
    # title="analytical",
    frameon=False,
    # loc="lower right",
    # bbox_to_anchor=(1, 0),
    handlelength=0.8,
    title="LE range",
)

plt.tight_layout()

# save to pdf
plt.savefig(FIGURE_FOLDER / f"irr_tp_factor_lapse.pdf", bbox_inches="tight")
