from os import path
from xml.etree.ElementTree import TreeBuilder
from numpy.core.numeric import full
from numpy.lib.twodim_base import triu_indices_from
import numpy as np
import matplotlib.pyplot as plt
import re  # regular expression
import pandas as pd

from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy, extendarray
from premiumFinance.fetchdata import getAnnualYield, getMarketSize
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.constants import DATA_FOLDER


mortality_experience_path = path.join(DATA_FOLDER, "mortalityexperience.xlsx")


def get_representative_age(x: str) -> int:
    return int(np.mean([int(x) for x in re.split("[+-]", x) if x != ""]))


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

profit_untapped = 0
breakeven_loanrate = []
lender_profit = []

for i, row in mortality_experience.iterrows():
    if i < 500:  # type: ignore
        print(i)
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
            premium_markup=0.15,
        )
        this_financing = PolicyFinancingScheme(this_policy)
        this_breakeven_loanrate = this_financing.breakevenLoanRate(fullrecourse=True)
        if not (0 < this_breakeven_loanrate < 1):
            this_breakeven_loanrate = np.nan
            this_lender_profit = 0
        else:
            this_lender_profit = this_financing.PV_lender(
                loanrate=this_breakeven_loanrate, fullrecourse=True
            )
        breakeven_loanrate.append(this_breakeven_loanrate)
        lender_profit.append(this_lender_profit)

mortality_experience["Breakeven Loan rate"] = breakeven_loanrate
mortality_experience["Lender profit"] = lender_profit


amount_exposed = mortality_experience["Amount Exposed "]

#%% total amount untapped
dollar_amount_untapped = (
    sum(amount_exposed * lender_profit) * getMarketSize(year=2020) / sum(amount_exposed)
)

untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")

mortality_experience.to_excel(untapped_profit_path, index=False)

profit_untapped_table = mortality_experience[
    [
        "isMale",
        "issueage",
        "currentage",
    ]
]

# this_profit = this_financing.PV_lender_maxed(levelPr=True, fullrecourse=True)
# print(this_insured)
# print(this_profit)
# profit_untapped += this_profit * row["Amount Exposed "]  # type: ignore
# print(profit_untapped)

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
    insPol0.statutory_interest = extendarray(sr)
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
                bkv_r = financing0.breakevenLoanRate(fullrecourse=True)
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
