# read irr_results.pickle


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

plt.rcParams.update({"font.size": 18})

plt.figure(figsize=(8, 6))


#  draw maxle vs aggregated_face with surface filled between the plotted line and 0
plt.fill_between(maxle_aggface.index, maxle_aggface / 10**scale_down, 0, alpha=0.3)
plt.ylabel(f"Lapsed economic value ({DOLLAR_MAGNITUDES[scale_down]} USD)")

plt.ylim(0, 194)
plt.xlabel("Life expectancy $\it LE$ (years)")


plt.tight_layout()

# save to FIGURE_FOLDER / "maxle_vs_ev_irr.pdf"
plt.savefig(FIGURE_FOLDER / "lapsed_ev_cdf.pdf")
