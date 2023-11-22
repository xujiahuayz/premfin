import numpy as np
import matplotlib.pyplot as plt

from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.fetchdata import get_annual_yield
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.util import make_list


insured_A8 = Insured(
    issue_age=54, is_male=True, is_smoker=False, current_age=None, issue_vbt="VBT01"
)

policy_A8 = InsurancePolicy(
    insured=insured_A8,
    is_level_premium=True,
    lapse_assumption=True,
    statutory_interest=0.05,
    premium_markup=0.15,
)

policy_A8_nolapse = InsurancePolicy(
    insured=insured_A8,
    is_level_premium=True,
    lapse_assumption=False,
    statutory_interest=0.05,
    premium_markup=0.15,
)

policy_A8._level_premium
# 0.012258309441970858
7821.8 / 750_000

policy_A8_nolapse._level_premium
# 0.020767438228614155

policy_A8._variable_premium
# [0.0,
#  0.0014175831113703672,
#  0.0021522114467532067,
#  0.00280132689213079,
#  0.0033613377249408056,
#  0.003873987707520262,
#  0.004551769450898281,

policy_A8_nolapse._variable_premium
# [0.0,
#  0.001324022626019923,
#  0.0019929477996934696,
#  0.0026164393172501575,

insrd_benchmark = Insured(
    issue_age=40,
    is_male=True,
    is_smoker=False,
    current_age=70,
    issue_mort=1.0,
    current_mort=1.0,
    issue_vbt="VBT01",
    current_vbt="VBT15",
)

insPol0 = InsurancePolicy(
    insured=insrd_benchmark,
    is_level_premium=True,
    lapse_assumption=True,
    policyholder_rate=get_annual_yield(year=2020),
    # surrender_penalty_rate=0.1,
    # cash_interest=0.05,
    # premium_markup=0.2,
    # statutory_interest=0.03,
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
            insrd_benchmark.current_mort = mort
            bkv_r_currentagelevel = list()
            for age in current_age_range:
                insrd_benchmark.current_age = age
                bkv_r = financing0.max_loan_rate_borrower(fullrecourse=True)[1]
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
            At issue: {insrd_benchmark.issue_age}-year-old, {'' if insrd_benchmark.is_smoker else 'non-'}smoking, {insrd_benchmark.mortality_at_issue.gender}, mortality factor: {insrd_benchmark.issue_mort}
            """
            f"""
            Lapse-based pricing: {lapse_range[j]}, statutory interest rate: {statutory_rate_rage[k]}, premium rate: {round(pr_statratelevel[k][j],4)}
            """
        )
        plt.show()
