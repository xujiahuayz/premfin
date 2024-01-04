import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER

wealth_path = DATA_FOLDER / "Wealth_tables_dy2019.xlsx"
wealth = pd.read_excel(wealth_path)
wealth = wealth.iloc[82:90, [0, 1, 18]]

# change column names to 'band', 'cv_life', 'median_asset'
column_names = ["band", "median_asset", "cv_life"]
wealth.columns = column_names
wealth["value"] = wealth["cv_life"] / wealth["median_asset"]
# replace "$" with "\$" for latex for the first column, and replace "to" with "-"
wealth["band"] = wealth["band"].str.replace("$", "\$").str.replace("to", "-")
# remove " and over" from the last value of wealth["band"] and add ">=" in front of it
wealth["band"].iloc[-1] = ">=" + wealth["band"].iloc[-1].replace(" and over", "")

X_labels = np.array(wealth.iloc[:, [0]])[:, 0]
heights = list(wealth["value"])
plt.bar(X_labels, height=heights, width=0.7, color="royalblue", label="value")
for x, y in enumerate(heights):
    plt.text(x, y, "%s" % round(y, 2), ha="center", va="bottom", fontsize=8)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(FIGURE_FOLDER / "wealth_distr.pdf")
plt.show()
