#%% import packages
import json
from os import path
import pandas as pd
import matplotlib.pyplot as plt

from premiumFinance.fetchdata import getMarketSize
from premiumFinance.constants import (
    DATA_FOLDER,
    MORTALITY_TABLE_CLEANED_PATH,
    PROCESSED_PROFITABILITY_PATH,
)
from premiumFinance.financing import calculate_lender_profit

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

#%% calculate percentage profit
profit_columns = mortality_experience.apply(
    lambda row: calculate_lender_profit(
        row=row,
    ),
    axis=1,
    result_type="expand",
)

mortality_experience[["Breakeven Loan rate", "Lender profit"]] = profit_columns

mortality_experience["Dollar profit"] = (
    mortality_experience["Lender profit"] * mortality_experience["Amount Exposed"]
)

mortality_experience["Dollar profit"].sum() / mortality_experience[
    "Amount Exposed"
].sum()

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)

#%% calculate dollar profit

mortality_experience["Lender profit"].mean()
mortality_experience["Dollar profit"].sum() / mortality_experience[
    "Amount Exposed"
].sum()
dollar_amount_untapped = (
    mortality_experience["Dollar profit"].sum()
    * getMarketSize(year=2020)
    / mortality_experience["Amount Exposed"].sum()
)

#%% plot
with open(PROCESSED_PROFITABILITY_PATH, "r") as f:
    profitability = json.load(f)
plt.plot(profitability["lender_coc"], profitability["profitability"][0], label="True")
plt.plot(profitability["lender_coc"], profitability["profitability"][1], label="False")
plt.xlabel("Lender cost of capital")
plt.ylabel("Maximum profit untapped (in fraction of face value)")
plt.legend(title="Lapse assumption")

# %%
