import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot as plt
from scipy import optimize
from copy import deepcopy
from time import time
import json

from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy, extendarray
from premiumFinance.mortality import Mortality
from premiumFinance.fetchdata import getAnnualYield
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.settings import PROJECT_ROOT
from premiumFinance.constants import DATA_FOLDER

insrd_benchmark = Insured(
    issueage=40,
    isMale=True,
    isSmoker=False,
    currentage=70,
    issuemort=1.0,
    currentmort=1.0,
)

insPol0 = InsurancePolicy(
    insrd=insrd_benchmark,
    lapse_assumption=True,
    policyholder_rate=getAnnualYield(),
    surrender_penalty_rate=0.1,
    cash_interest=0.05,
    prmarkup=0.2,
    statutory_interest=0.03,
)

insPol0.getLevelpr()
insPol0.plotPersRate()
plt.close()
insPol0.plotPersRate(atIssue=False)
insPol0.PV_db(issuerPerspective=True)
insPol0.PV_db(issuerPerspective=False, assumeLapse=False)


financing0 = PolicyFinancingScheme(insPol0)

current_age_range = np.arange(40, 90, 2)
current_mort_range = np.arange(0.5, 1.6, 0.5)
statrate_range = [0.01, 0.1]
lapse_range = [True, False]

bkv_r_statratelevel = list()
pr_statratelevel = list()
for sr in statrate_range:
    insPol0.statutory_interest = extendarray(sr)
    bkv_r_lapselevel = list()
    pr_lapselevel = list()
    for assumelapse in lapse_range:
        insPol0.lapse_assumption = assumelapse
        pr = financing0.policy.getLevelpr(assumeLapse=assumelapse, newPolicy=False)
        bkv_r_mortlevel = list()
        for mort in current_mort_range:
            insrd_benchmark.currentmort = mort
            bkv_r_currentagelevel = list()
            for age in current_age_range:
                insrd_benchmark.currentage = age
                bkv_r = financing0.breakevenLoanRate(pr=pr)
                bkv_r_currentagelevel.extend([bkv_r])
                print(age)
            bkv_r_mortlevel.append(bkv_r_currentagelevel)
            print(str(mort) + "========")
        bkv_r_lapselevel.append(bkv_r_mortlevel)
        pr_lapselevel.extend([pr])
    bkv_r_statratelevel.append(bkv_r_lapselevel)
    pr_statratelevel.append(pr_lapselevel)

for k, v in enumerate(bkv_r_statratelevel):
    for j, w in enumerate(v):
        for i, x in enumerate(w):
            plt.plot(current_age_range, x, label=round(current_mort_range[i], 1))
            plt.ylim([0, 1])
        plt.legend(title="Current mortality factor", loc="upper left")
        plt.xlabel("Current age")
        plt.ylabel("Breakeven loan rate p.a.")
        plt.title(
            f"""
            At issue: {insrd_benchmark.issueage}-year-old, {'' if insrd_benchmark.isSmoker else 'non-'}smoking, {insrd_benchmark.issueMort().gender()}, mortality factor: {insrd_benchmark.issuemort}
            """
            f"""
            Lapse-based pricing: {lapse_range[j]}, statutory interest rate: {statrate_range[k]}, premium rate: {pr_statratelevel[k][j]}
            """
        )
        plt.show()
        plt.close()


# with open(path.join(PROJECT_ROOT, DATA_FOLDER, "bkv_r_matrix.json"), "w") as f:
#     json.dump(bkv_r_matrix, f, indent=2)

# bkv_r_matrix2 = json.load(
#     open(path.join(PROJECT_ROOT, DATA_FOLDER, "bkv_r_matrix.json"), "r")
# )


insPol1 = InsurancePolicy(
    insrd=insrd_benchmark,
    lapse_assumption=False,
    policyholder_rate=0.001,
    surrender_penalty_rate=0.1,
)
insPol2 = InsurancePolicy(
    insrd=insrd_benchmark,
    lapse_assumption=False,
    policyholder_rate=getAnnualYield(),
    surrender_penalty_rate=0.1,
)


sttime = time()
# pv_deathben = financing3.PV_db()
financing0.breakevenLoanRate(pr=pr)
print(time() - sttime)

sttime = time()
financing0.breakevenLoanRate()
print(time() - sttime)


financing0.surrender_value(levelPr=True)
financing0.PV_borrower(levelPr=False, loanrate=0.01, nonrecourse=False)
financing0.PV_lender(levelPr=False, loanrate=0.01, nonrecourse=True)


insrd_oldcurrent = deepcopy(insrd_benchmark)
insrd_oldcurrent.currentage = 50


insrd_oldissue = deepcopy(insrd_benchmark)
insrd_oldissue.currentage = 90


insrd_fem = deepcopy(insrd_benchmark)
insrd_fem.isMale = False


insrd_smoker = deepcopy(insrd_benchmark)
insrd_smoker.isSmoker = True


insrd_sickissue = deepcopy(insrd_benchmark)
insrd_sickissue.issueMort = 1.2


insrd_sickcurrent = deepcopy(insrd_benchmark)
insrd_sickcurrent.currentmort = 1.2
