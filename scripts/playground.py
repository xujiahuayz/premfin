#%% import packages
from os import path
from xml.etree.ElementTree import TreeBuilder
from numpy.core.numeric import full
from numpy.lib.twodim_base import triu_indices_from
import numpy as np
import matplotlib.pyplot as plt
import re  # regular expression
import pandas as pd

from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.fetchdata import getAnnualYield, getMarketSize
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.constants import DATA_FOLDER
from premiumFinance.util import make_list

#%% define functions


def get_representative_age(x: str) -> int:
    return int(np.mean([int(x) for x in re.split("[+-]", x) if x != ""]))


yield_curve = getAnnualYield()


def calculate_lender_profit(
    row,
    is_level_premium=True,
    lapse_assumption=True,
    policyholder_rate=yield_curve,
    statutory_interest=0.035,
    premium_markup=0.0,
    cash_interest=0.001,
    lender_coc=0.01,
):
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
        is_level_premium=is_level_premium,
        lapse_assumption=lapse_assumption,
        statutory_interest=statutory_interest,
        premium_markup=premium_markup,
        policyholder_rate=policyholder_rate,
        cash_interest=cash_interest,
    )
    this_financing = PolicyFinancingScheme(this_policy, lender_coc=lender_coc)
    this_breakeven_loanrate = this_financing.max_loan_rate_borrower(fullrecourse=True)
    if not (0.0 < this_breakeven_loanrate < 1.0):
        this_breakeven_loanrate = np.nan
        this_lender_profit = 0.0
        # else:
    elif isinstance(lender_coc, (int, float)) and this_breakeven_loanrate <= lender_coc:
        this_lender_profit = 0.0
    else:
        this_lender_profit = this_financing.PV_lender(
            loanrate=this_breakeven_loanrate, fullrecourse=True
        )
        # assert (
        #     0.0 <= this_lender_profit <= 1.0
        # ), f"lender profit must fall in (0,1), cohort profile: {row}"
    return this_breakeven_loanrate, max(this_lender_profit, 0.0)


#%% prepare datatable
mortality_experience_path = path.join(DATA_FOLDER, "mortalityexperience.xlsx")

mortality_experience = pd.read_excel(mortality_experience_path)

mortality_experience["issueage"] = mortality_experience["Issue Age Group"].map(
    get_representative_age
)
mortality_experience["currentage"] = mortality_experience["Attained Age Group"].map(
    get_representative_age
)
mortality_experience["isMale"] = mortality_experience["Gender"].map(
    lambda x: True if x == "Male" else False
)
mortality_experience["isSmoker"] = mortality_experience["Smoker Status"].map(
    lambda x: {"NonSmoker": False, "Smoker": True, "Unknown": None}[x]
)

#%% calculate profit rate
profit_columns = mortality_experience.apply(
    lambda row: calculate_lender_profit(
        row=row,
        is_level_premium=True,
        lapse_assumption=True,
        policyholder_rate=yield_curve,
        statutory_interest=0.035,
        premium_markup=0.15,
        cash_interest=0.001,
        lender_coc=0.01,
    ),
    axis=1,
    result_type="expand",
)

#%% calculate dollar profit
profit_columns[0].sum() / profit_columns[1].sum()
profit_columns[0].sum() * getMarketSize(year=2020) / profit_columns[1].sum()


#%% save to excel
mortality_experience[["Breakeven Loan rate", "Lender profit"]] = profit_columns

mortality_experience["Dollar profit"] = (
    mortality_experience["Lender profit"] * mortality_experience["Amount Exposed "]
)

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")
mortality_experience.to_excel(untapped_profit_path, index=False)
#%% calculate dollar profit

mortality_experience["Lender profit"].mean()
dollar_amount_untapped = (
    mortality_experience["Dollar profit"].sum()
    * getMarketSize(year=2020)
    / mortality_experience["Amount Exposed "].sum()
)


# mortality_experience["Dollar profit"].sum() / mortality_experience[
#     "Amount Exposed "
# ].sum()

#%% spot check

insured_A8 = Insured(
    issue_age=54, isMale=True, isSmoker=False, current_age=None, issueVBT="VBT01"
)

policy_A8 = InsurancePolicy(
    insured=insured_A8,
    is_level_premium=True,
    lapse_assumption=True,
    statutory_interest=0.05,
    premium_markup=0.15,
)

policy_A8._level_premium
7821.8 / 750_000

#%% exploratory plots
insrd_benchmark = Insured(
    issue_age=40,
    isMale=True,
    isSmoker=False,
    current_age=70,
    issuemort=1.0,
    currentmort=1.0,
    issueVBT="VBT01",
    currentVBT="VBT15",
)

insPol0 = InsurancePolicy(
    insured=insrd_benchmark,
    is_level_premium=True,
    lapse_assumption=True,
    policyholder_rate=getAnnualYield(),
    surrender_penalty_rate=0.1,
    cash_interest=0.05,
    premium_markup=0.2,
    statutory_interest=0.03,
)

insPol0._level_premium

financing0 = PolicyFinancingScheme(insPol0)


current_age_range = np.arange(40, 90, 2)
current_mort_range = np.arange(0.5, 1.6, 0.5)
statutory_rate_rage = [0.01, 0.1]
lapse_range = [True, False]

bkv_r_statratelevel = list()
pr_statratelevel = list()
for sr in statutory_rate_rage:
    insPol0.statutory_interest = make_list(sr)
    bkv_r_lapselevel = list()
    premium_level = list()
    for assumelapse in lapse_range:
        insPol0.lapse_assumption = assumelapse
        pr = financing0.policy._level_premium
        bkv_r_mortlevel = list()
        for mort in current_mort_range:
            insrd_benchmark.currentmort = mort
            bkv_r_currentagelevel = list()
            for age in current_age_range:
                insrd_benchmark.current_age = age
                bkv_r = financing0.max_loan_rate_borrower(fullrecourse=True)
                bkv_r_currentagelevel.append(bkv_r)
                print(age)
            bkv_r_mortlevel.append(bkv_r_currentagelevel)
            print(str(mort) + "========")
        bkv_r_lapselevel.append(bkv_r_mortlevel)
        premium_level.append(pr)
    bkv_r_statratelevel.append(bkv_r_lapselevel)
    pr_statratelevel.append(premium_level)

for k, v in enumerate(bkv_r_statratelevel):
    for j, w in enumerate(v):
        plt.close()
        for i, x in enumerate(w):
            plt.plot(current_age_range, x, label=round(current_mort_range[i], 1))
            plt.ylim([0, 1])
        plt.legend(title="Current mortality factor", loc="upper left")
        plt.xlabel("Current age")
        plt.ylabel("Breakeven loan rate p.a.")
        plt.title(
            f"""
            At issue: {insrd_benchmark.issue_age}-year-old, {'' if insrd_benchmark.isSmoker else 'non-'}smoking, {insrd_benchmark.mortality_at_issue.gender}, mortality factor: {insrd_benchmark.issuemort}
            """
            f"""
            Lapse-based pricing: {lapse_range[j]}, statutory interest rate: {statutory_rate_rage[k]}, premium rate: {round(pr_statratelevel[k][j],4)}
            """
        )
        plt.show()
