#%% import packages
import numpy as np
from os import path
import pandas as pd
import matplotlib.pyplot as plt

from premiumFinance.fetchdata import getMarketSize
from premiumFinance.constants import (
    DATA_FOLDER,
)
from premiumFinance.financing import (
    calculate_policyholder_IRR,
    Insured,
    InsurancePolicy,
    PolicyFinancingScheme,
)

IRR_PATH = path.join(DATA_FOLDER, "irrs.xlsx")

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")
mortality_experience = pd.read_excel(untapped_profit_path)


#%% calculate irr -- slightly time consuming
irr_columns = mortality_experience.apply(
    lambda row: calculate_policyholder_IRR(
        row=row,
    ),
    axis=1,
    result_type="expand",
)

irr_columns.to_excel(IRR_PATH, index=False)

irr_columns = pd.read_excel(IRR_PATH)
mortality_experience["Policyholder IRR"] = irr_columns


mortality_experience["Dollar profit"].sum() / mortality_experience[
    "Amount Exposed"
].sum()


mortality_experience["Lender profit"].mean()
mortality_experience["Dollar profit"].sum() / mortality_experience[
    "Amount Exposed"
].sum()
sample_representativeness = (
    getMarketSize(year=2020) / mortality_experience["Amount Exposed"].sum()
)

dollar_amount_untapped = (
    mortality_experience["Dollar profit"].sum() * sample_representativeness
)

#%% exploratory plot
row = mortality_experience.iloc[23]
this_insured = Insured(
    issue_age=row["issueage"],  # type: ignore
    is_male=row["isMale"],  # type: ignore
    is_smoker=row["isSmoker"],  # type: ignore
    current_age=row["currentage"],  # type: ignore
    issue_vbt="VBT01",
    current_vbt="VBT15",
)
this_policy = InsurancePolicy(
    insured=this_insured,
    is_level_premium=True,
    lapse_assumption=True,
    statutory_interest=0.035,
    premium_markup=0.0,
    # TODO: show https://www.forbes.com/advisor/life-insurance/universal-life-insurance/
    cash_interest=0.03,
)
this_financing = PolicyFinancingScheme(this_policy)
sv = this_financing.surrender_value()  # =  0
policy_val = []
r_range = np.arange(start=-0.01, stop=2, step=0.01)
for r in r_range:
    policy_val.append(
        -this_policy.policy_value(
            discount_rate=r, issuer_perspective=False, at_issue=False
        )
    )

plt.plot(r_range, policy_val)
plt.axhline(y=0, c="r")
plt.show()
