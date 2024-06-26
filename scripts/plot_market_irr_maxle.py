# read irr_results.pickle

import pickle

from matplotlib import pyplot as plt
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER

import pandas as pd

# unpickle DATA_FOLDER / "irr_results_maxle.pickle" to dataframe

results = pd.read_pickle(DATA_FOLDER / "irr_results_maxle.pickle")
# make it a dataframe
results = pd.DataFrame(results)


maxle_aggface = results.groupby("maxle")["ev"].mean()
plt.figure(figsize=(10, 6))

#  draw maxle vs aggregated_face with surface filled between the plotted line and 0
plt.fill_between(maxle_aggface.index, maxle_aggface, 0, alpha=0.3)
plt.ylabel("Aggregated EEV")
# plot irr in the same graph on a different y axis
plt.twinx()

for tp_factor in [0]:
    newdf = results[results["tp_factor"] == tp_factor]
    plt.plot(newdf["maxle"], newdf["irr"], label=f"tp_factor: {tp_factor}")

plt.xlabel("Max Life Expectancy")
plt.ylabel("IRR")
plt.legend()
