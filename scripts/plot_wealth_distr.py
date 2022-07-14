from os import path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER

#%%
wealth_path = path.join(DATA_FOLDER, "Wealth_tables_dy2019.xlsx")
wealth = pd.read_excel(wealth_path)
wealth = wealth.iloc[82:90, [0, 1, 18]]
wealth["value"] = wealth["Unnamed: 18"] / wealth["Unnamed: 1"]
X_labels = np.array(wealth.iloc[:, [0]])[:, 0]
heights = list(wealth["value"])
plt.bar(X_labels, height=heights, width=0.7, color="royalblue", label="value")
for x, y in enumerate(heights):
    plt.text(x, y, "%s" % round(y, 2), ha="center", va="bottom", fontsize=8)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(path.join(FIGURE_FOLDER, "wealth_distr.pdf"))
plt.show()
