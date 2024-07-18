# read irr_results.pickle

import pickle

from matplotlib import pyplot as plt
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER, DOLLAR_MAGNITUDES

import pandas as pd
import matplotlib.lines as mlines


scale_down = 9

# unpickle DATA_FOLDER / "irr_results_maxle.pickle" to dataframe

results = pd.read_pickle(DATA_FOLDER / "irr_results_maxle.pickle")
# make it a dataframe
results = pd.DataFrame(results)


maxle_aggface = results.groupby("maxle")["ev"].mean()


line_types = {0: "-", 0.1: "--", 0.2: ":"}
colors = {0: "red", 0.5: "blue", 1: "green", 1.5: "orange"}


pm_handle = [
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
        label=tp_factor,
    )
    for tp_factor, color in colors.items()
]


# increase font size
# adjust figure size to make sure that the labels are not cut off, especially for the y axis on the right

plt.rcParams.update({"font.size": 20})

plt.figure(figsize=(8, 6))


#  draw maxle vs aggregated_face with surface filled between the plotted line and 0
plt.fill_between(maxle_aggface.index, maxle_aggface / 10**scale_down, 0, alpha=0.3)
plt.ylabel(f"Lapsed economic value ({DOLLAR_MAGNITUDES[scale_down]} USD)")

plt.ylim(0, 194)
plt.xlabel("Max life expectancy in the portfolio $\max(LE)$ (years)")

# plot irr in the same graph on a different y axis
plt.twinx()


for premium_markup, line_style in line_types.items():
    for tp_factor, color in colors.items():
        # get the position of tp_factor for color
        newdf = results[
            (results["tp_factor"] == tp_factor)
            & (results["premium_markup"] == premium_markup)
        ]
        plt.plot(
            newdf["maxle"],
            newdf["irr"],
            # label=f"${tp_factor}$",
            linestyle=line_style,
            color=color,
        )

# ylimit -0.8 to 0.9

# log scale for y axis
plt.yscale("log")

plt.ylim(0.06, 0.9)
# add tick marks for y axis with numbers

plt.yticks(
    [0.06, 0.08, 0.1, 0.2, 0.3, 0.6],
    [0.06, 0.08, 0.1, 0.2, 0.3, 0.6],
)

plt.ylabel("IRR")

first_legend = plt.legend(
    handles=pm_handle,
    frameon=False,
    loc="upper left",
    # bbox_to_anchor=(1, 1),
    handlelength=0.8,
    title="premium markup $\Delta$",
)

plt.gca().add_artist(first_legend)
plt.legend(
    handles=tp_factor_handle,
    # title="analytical",
    frameon=False,
    loc="upper right",
    # bbox_to_anchor=(1, 0),
    handlelength=0.8,
    title="price factor $\kappa$",
)


# do two set of legend, one for premium markup (line types)
# and one for tp_factor (colors)


# plt.legend(title="price factor $\kappa$", handlelength=1)
# tight layout
plt.tight_layout()

# save to FIGURE_FOLDER / "maxle_vs_ev_irr.pdf"
plt.savefig(FIGURE_FOLDER / "maxle_vs_ev_irr.pdf")
