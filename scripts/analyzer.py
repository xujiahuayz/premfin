from mortfuncs import *
from numpy import linspace
import matplotlib.pyplot as plt


def explore_plot(rFree, age_v, pr_v):

    surv_v = getSurcurv(isMale=False, age=age_v)

    pv_pr = getPV_pr(pr=pr_v, surv=surv_v)
    pv_db = getPV_db(surv=surv_v)

    pv_financer_nr = []
    pv_polholder_nr = []

    pv_financer_fr = []
    pv_polholder_fr = []
    # borrow rate
    rB_vs = rFree+linspace(0, 0.3, 101)

    for rB in rB_vs:
        pv_debt = getPV_endpay(pr=pr_v, surv=surv_v, r_b=rB)
        pv_financer, pv_polholder = getPV_agents(finop='nonrecourse', pv_db_value=pv_db,
                                                 pv_pr_value=pv_pr, pv_debt_value=pv_debt)
        pv_financer_nr.append(pv_financer)
        pv_polholder_nr.append(pv_polholder)

        pv_financer, pv_polholder = getPV_agents(finop='fullrecourse', pv_db_value=pv_db,
                                                 pv_pr_value=pv_pr, pv_debt_value=pv_debt)
        pv_financer_fr.append(pv_financer)
        pv_polholder_fr.append(pv_polholder)

    # fig, ax = plt.subplots()
    plt.plot(rB_vs, pv_financer_nr, label='Nonrecourse financer', c='green')
    plt.plot(rB_vs, pv_polholder_nr,
             label='Nonrecourse policyholder', c='orange')

    plt.plot(rB_vs, pv_financer_fr, linestyle='--',
             label='Fullrecourse financer', c='green')
    plt.plot(rB_vs, pv_polholder_fr, linestyle='--',
             label='Fullrecourse policyholder', c='orange')

    plt.axhline(pv_pr - pv_db, c='red', label='Insurer')

    plt.axhline(0, c='grey', linewidth=0.5)
    plt.xlabel('borrow rate')
    plt.ylabel('present value')
    plt.legend()
    plt.title(
        'risk-free rate: ' + str(rFree) + '\n annual premium rate: ' +
        str(pr_v) + '\n age: ' + str(age_v)
    )
    plt.show()
    plt.close()


# risk-free rate
# rFree = 0.005
# age_v = 75
# pr_v = 0.002
explore_plot(rFree=0.005, age_v=75, pr_v=0.002)
explore_plot(rFree=0.01, age_v=75, pr_v=0.002)

explore_plot(rFree=0.01, age_v=85, pr_v=0.02)

explore_plot(rFree=0.01, age_v=55, pr_v=0.0001)

explore_plot(rFree=0.07, age_v=85, pr_v=0.02)
explore_plot(rFree=0.01, age_v=85, pr_v=0.02)
explore_plot(rFree=0.01, age_v=85, pr_v=0.01)
explore_plot(rFree=0.01, age_v=85, pr_v=0.008)
