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
from premiumFinance.financing import (
    yield_curve,
    calculate_lender_profit,
    calculate_policyholder_IRR,
    policyholder_policy_value,
)

IRR_PATH = path.join(DATA_FOLDER, "irrs.xlsx")
PROFIT_PATH = path.join(DATA_FOLDER, "profits.xlsx")


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
    # TODO: check a realistic cash interest from 2010-2015
    cash_interest=0.001,
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


#%% calculate irr -- slightly time consuming
irr_columns = mortality_experience.apply(
    lambda row: calculate_policyholder_IRR(
        row=row,
    ),
    axis=1,
    result_type="expand",
)

irr_columns.to_excel(IRR_PATH, index=False)


#%% calculate percentage profit -- slightly time consuming
profit_columns = mortality_experience.apply(
    lambda row: calculate_lender_profit(
        row=row,
    ),
    axis=1,
    result_type="expand",
)

profit_columns.to_excel(PROFIT_PATH, index=False)


#%% calculate policy PV from perspective of policyholder

mortality_experience["Excess_Policy_PV_yield_curve"] = (
    mortality_experience.apply(
        lambda row: policyholder_policy_value(row=row, policyholder_rate=yield_curve),
        axis=1,
        result_type="expand",
    )
    - pd.read_excel(PROFIT_PATH)[0]
)

for i in [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
    print(i)
    mortality_experience[f"Excess_Policy_PV_{i}"] = (
        mortality_experience.apply(
            lambda row: policyholder_policy_value(row=row, policyholder_rate=i),
            axis=1,
            result_type="expand",
        )
        - pd.read_excel(PROFIT_PATH)[0]
    )
# PROFIT_PATH = path.join(DATA_FOLDER, "profits.xlsx")
# profit_columns.to_excel(PROFIT_PATH, index=False)

#%% post-process

irr_columns = pd.read_excel(IRR_PATH)
mortality_experience["Policyholder IRR"] = irr_columns

profit_columns = pd.read_excel(PROFIT_PATH)
mortality_experience[
    ["Surrender value", "Max Loan rate", "Lender profit"]
] = profit_columns

mortality_experience["Dollar profit"] = (
    mortality_experience["Lender profit"] * mortality_experience["Amount Exposed"]
)

mortality_experience["Dollar profit"].sum() / mortality_experience[
    "Amount Exposed"
].sum()

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)


#%% calculate dollar profit

mortality_experience = pd.read_excel(untapped_profit_path)

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


money_left_array = []
investor_coc = [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, "yield_curve"]
for i in investor_coc:
    money_left = (
        sum(
            w
            for w in mortality_experience[f"Excess_Policy_PV_{i}"]
            * mortality_experience["Amount Exposed"]
            if w > 0
        )
        * sample_representativeness
    )
    money_left_array.append(money_left)

    print(
        f"when policyholder rate equals {i}, total money left on the table: {money_left}"
    )

#%% money left plot

# https://www.federalreserve.gov/releases/z1/20120607/z1.pdf page 113
real_estate_nominal = 23523.6 / 1e3

# change from 2007-2009
real_estate_change = (23523.6 - 18874.5) / 1e3

WIDTH = 1

plt.bar(x=0, height=real_estate_nominal)

plt.bar(x=WIDTH, height=[getMarketSize(year=2020) / 1e12])


plt.xticks(
    [0, WIDTH],
    [
        "Real estate",
        "Life insurance",
    ],
    rotation=90,
)
plt.ylabel("trillion USD")


plt.show()

plt.bar(x=0, height=real_estate_change)

plt.bar(x=WIDTH, height=money_left_array[-1] / 1e12)


plt.xticks(
    [0, WIDTH],
    [
        "Real estate value loss",
        "Life insurance money left",
    ],
    rotation=90,
)
plt.ylabel("trillion USD")

#%% old plot plot
plt.bar(
    x=0,
    height=real_estate_nominal,
    width=WIDTH,
    color="blue",
    edgecolor="k",
)

plt.bar(
    x=WIDTH,
    height=real_estate_change,
    width=WIDTH,
    color="green",
    edgecolor="k",
)


x_pos = np.arange(len(money_left_array))

plt.bar(
    x=3 * WIDTH,
    height=[getMarketSize(year=2020) / 1e12],
    width=WIDTH,
    color="blue",
    edgecolor="k",
    # tick_label=["Total Face"],
)

plt.bar(
    x=x_pos + 4 * WIDTH,
    height=np.array(money_left_array) / 1e12,
    width=WIDTH,
    color="green",
    edgecolor="k",
    # tick_label=investor_coc,
)

plt.xticks(
    [0, WIDTH, 3 * WIDTH] + (x_pos + 4 * WIDTH).tolist(),
    [
        "Real estate",
        "Value lost",
        "Life insurance",
    ]
    + investor_coc,
    rotation=90,
)
plt.ylabel("trillion USD")

# fig, ax = plt.subplots()


#%% plot
with open(PROCESSED_PROFITABILITY_PATH, "r") as f:
    profitability = json.load(f)
plt.plot(profitability["lender_coc"], profitability["profitability"][0], label="True")
plt.plot(profitability["lender_coc"], profitability["profitability"][1], label="False")
plt.xlabel("Lender cost of capital")
plt.ylabel("Maximum profit untapped (in fraction of face value)")
plt.legend(title="Lapse assumption")
