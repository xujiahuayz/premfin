import pandas as pd

from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH
from premiumFinance.financing import PolicyFinancingScheme, yield_curve
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured


current_vbt: str = "VBT15"
current_mort: float = 1.0
is_level_premium=True
lapse_assumption=True
policyholder_rate=yield_curve
statutory_interest: float = 0.035
premium_markup: float = 0.0
cash_interest: float = 0.073
premium_hike: float = 0.0
issue_age = 18
current_age = issue_age

this_insured = Insured(
    issue_age=issue_age,
    is_male=False,
    is_smoker=False,
    current_age=current_age,
    issue_vbt="VBT01",
    current_vbt=current_vbt,
    current_mortality_factor=current_mort,
)

# premium markup = 0 for default case to calculate
this_policy = InsurancePolicy(
    insured=this_insured,
    is_level_premium=is_level_premium,
    lapse_assumption=lapse_assumption,
    statutory_interest=statutory_interest,
    premium_markup=premium_markup,
    policyholder_rate=policyholder_rate,
    cash_interest=cash_interest,
)
this_financing = PolicyFinancingScheme(policy=this_policy)


sv_values = []
ev_values = []
age_values = []
while this_insured.current_age < 100:
    age_values.append(this_insured.current_age)

    sv = this_financing.surrender_value()
    ev = -this_policy.policy_value(
                issuer_perspective=False,
                at_issue=False,
                discount_rate=policyholder_rate,
            )

    sv_values.append(sv)
    ev_values.append(ev)


    this_insured.current_age += 1

# plot sv and ev

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
plt.figure(figsize=(10, 6))
plt.plot(age_values, sv_values, label="Surrender Value")
plt.plot(age_values, ev_values, label="Economic Value")
# horizontal line at 0
plt.axhline(0, color="black", linestyle="--")
plt.xlabel("Age")
plt.ylabel("Value")
plt.title("Surrender Value and Economic Value")
plt.legend()
