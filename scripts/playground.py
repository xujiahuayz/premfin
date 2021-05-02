from numpy.lib.twodim_base import triu_indices_from
import numpy as np
import matplotlib.pyplot as plt

from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy, extendarray
from premiumFinance.fetchdata import getAnnualYield
from premiumFinance.financing import PolicyFinancingScheme

insured_A8 = Insured(
    issueage=54, isMale=True, isSmoker=False, currentage=None, issueVBT="VBT01"
)

policy_A8 = InsurancePolicy(
    insrd=insured_A8,
    lapse_assumption=True,
    statutory_interest=0.05,
    prmarkup=0.15,
)

policy_A8.getLevelpr()
7821.8 / 750_000


insrd_benchmark = Insured(
    issueage=40,
    isMale=True,
    isSmoker=False,
    currentage=70,
    issuemort=1.0,
    currentmort=1.0,
    issueVBT="VBT01",
    currentVBT="VBT15",
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

financing0.PV_lender(loanrate=0.16754701834676933, fullrecourse=True)
financing0.breakevenLoanRate(fullrecourse=False, levelPr=True, surPenalty=None)

financing0.surrender_value(levelPr=True, surPenalty=None)
financing0.PV_borrower(loanrate=0.1675470183467693, levelPr=True, fullrecourse=True)

financing0.PV_lender_maxed(fullrecourse=False, levelPr=True, surPenalty=None)


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
                bkv_r = financing0.breakevenLoanRate(pr=pr, fullrecourse=False)
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
        plt.close()
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
            Lapse-based pricing: {lapse_range[j]}, statutory interest rate: {statrate_range[k]}, premium rate: {round(pr_statratelevel[k][j],4)}
            """
        )
        plt.show()
