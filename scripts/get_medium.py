# COL_NAMES = ["Gender", "Smoker Status",	"Issue Age", "Attained Age", "Amount Exposed", 	Policies Exposed 	Death Claim Amount 	Sum of Number of Deaths
from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER
from premiumFinance.fetchdata import getMarketSize
from premiumFinance.util import lapse_rate

import pandas as pd
from os import path
import matplotlib.pyplot as plt


untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")

mortality_experience = pd.read_excel(untapped_profit_path)

mortality_experience["lapse_rate"] = mortality_experience.apply(
    lambda row: lapse_rate(isMale=row["isMale"])[row["currentage"] - row["issueage"]],
    axis=1,
)


mortality_experience["number_lapsed_policies"] = (
    mortality_experience["lapse_rate"] * mortality_experience["Policies Exposed"]
)

mortality_experience["average_lapsed_amount"] = (
    mortality_experience["Excess_Policy_PV_yield_curve"]
    * mortality_experience["Amount Exposed"]
    / mortality_experience["Policies Exposed"]
)

mortality_experience_sorted = mortality_experience.sort_values(
    by=["average_lapsed_amount"], ignore_index=True
)

mortality_experience_sorted["number_policies_cumsum"] = mortality_experience_sorted[
    "number_lapsed_policies"
].cumsum()

medium_value_lapsed = mortality_experience_sorted.loc[
    (
        mortality_experience_sorted["number_policies_cumsum"]
        > mortality_experience_sorted["number_policies_cumsum"].iloc[-1] / 2
    ).values,
    "average_lapsed_amount",
].iat[0]
# 46190.03282643981
