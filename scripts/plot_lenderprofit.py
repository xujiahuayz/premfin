# %% import packages
import json
import matplotlib.pyplot as plt

from premiumFinance.constants import (
    PROCESSED_PROFITABILITY_PATH,
)

# %% plot
with open(PROCESSED_PROFITABILITY_PATH, "r") as f:
    profitability = json.load(f)
plt.plot(profitability["lender_coc"], profitability["profitability"][0], label="True")
plt.plot(profitability["lender_coc"], profitability["profitability"][1], label="False")
plt.xlabel("Lender cost of capital")
plt.ylabel("Maximum profit untapped (in fraction of face value)")
plt.legend(title="Lapse assumption")
