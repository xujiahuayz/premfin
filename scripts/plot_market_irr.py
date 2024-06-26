# read irr_results.pickle

import pickle

from matplotlib import pyplot as plt
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER

with open(DATA_FOLDER / "irr_results.pickle", "rb") as f:
    results = pickle.load(f)

for premium_markup in [0]:
    for mort_mult in [3]:
        # plot tp_factor (x) vs irr (y), each range as a line plot
        plt.figure(figsize=(10, 6))
        for ranges in [
            (0, 100),
            (0, 30),
            (50, 100),
        ]:
            x = []
            y = []

            for result in results:
                if (
                    result["premium_markup"] == premium_markup
                    and result["mort_mult"] == mort_mult
                    and result["ranges"] == ranges
                ):
                    x.append(result["tp_factor"])
                    y.append(result["irr"])

            plt.plot(x, y, label=f"LE range: {ranges}")
            # print(ranges)
            # print(y)
        # horizontal line at 0
        plt.axhline(0, color="black", linestyle="--")

        plt.xlabel(
            "Transaction price rate in excess of withdrawable surrender value rate"
        )
        plt.ylabel("IRR")
        plt.legend()

        plt.title(f"mort_mult: {mort_mult}, premium_markup: {premium_markup}")
