#%% import packages
import json
from os import path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from premiumFinance.financing import InsurancePolicy, Insured, PolicyFinancingScheme
from premiumFinance.fetchdata import getMarketSize
from premiumFinance.constants import (
    DATA_FOLDER,
    MORTALITY_TABLE_CLEANED_PATH,
    PROCESSED_PROFITABILITY_PATH,
)
from premiumFinance.financing import calculate_lender_profit, calculate_policyholder_IRR

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

#%% exploratory plot
row = mortality_experience.iloc[23]
this_insured = Insured(
    issue_age=row["issueage"],  # type: ignore
    isMale=row["isMale"],  # type: ignore
    isSmoker=row["isSmoker"],  # type: ignore
    current_age=row["currentage"],  # type: ignore
    issueVBT="VBT01",
    currentVBT="VBT15",
)
this_policy = InsurancePolicy(
    insured=this_insured,
    is_level_premium=True,
    lapse_assumption=True,
    statutory_interest=0.035,
    premium_markup=0.0,
    cash_interest=0.001,
)
this_financing = PolicyFinancingScheme(this_policy)
sv = this_financing.surrender_value()  # =  0
policy_val = []
r_range = np.arange(start=-0.01, stop=2, step=0.001)
for r in r_range:
    policy_val.append(
        -this_policy.policy_value(
            discount_rate=r, issuer_perspective=False, at_issue=False
        )
    )

plt.plot(r_range, policy_val)
plt.axhline(y=0)


#%% calculate irr -- slightly time consuming
irr_columns = mortality_experience.apply(
    lambda row: calculate_policyholder_IRR(
        row=row,
    ),
    axis=1,
    result_type="expand",
)

#%% calculate percentage profit -- slightly time consuming
profit_columns = mortality_experience.apply(
    lambda row: calculate_lender_profit(
        row=row,
    ),
    axis=1,
    result_type="expand",
)

#%% post-process

mortality_experience["Policyholder IRR"] = irr_columns
mortality_experience[["Max Loan rate", "Lender profit"]] = profit_columns

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
