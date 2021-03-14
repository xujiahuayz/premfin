from mortfuncs import *
from numpy import linspace
import matplotlib.pyplot as plt
from fetchdata import getAnnualYield


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


if __name__ == '__main__':

agerange = range(70,110)

prem_tbl = pickle.load(open(path.join(DATA_FOLDER,'empPrem.pkl'), 'rb'))
prem_ratio = prem_tbl[agerange].divide(prem_tbl['FA'], axis = 'index')

def plotEmpPrem(age: int, agetolerance: int = 5):
    select = abs(prem_tbl.IssueAge - age) < agetolerance

    prem_tbl_plot = prem_tbl[select]
    prem_tbl_plot_mean = prem_tbl_plot.mean()

    plt.plot(agerange, prem_ratio[select].mean(), label = 'absolute mean')
    plt.plot(agerange, prem_tbl_plot_mean[agerange] / prem_tbl_plot_mean['FA'], label = 'FA-weighted mean')
    plt.legend(title = 'averaging method')
    plt.ylabel('annual premium rate')
    plt.xlabel('insured age')
    plt.title(f'Issurance age: ${age} \pm {agetolerance}$')

plotEmpPrem(80)


def plotEmpPrembyMethod(ages, method, prem_tbl = prem_tbl, agetolerance: int = 5):
    for age in ages:
        select = abs(prem_tbl.IssueAge - age) < agetolerance

        prem_tbl_plot = prem_tbl[select]
        prem_tbl_plot_mean = prem_tbl_plot.mean()

        if method == 'FA-weighted':
            y = prem_tbl_plot_mean[agerange] / prem_tbl_plot_mean['FA']

        if method == 'absolute':
            prem_ratio = prem_tbl[agerange].divide(prem_tbl['FA'], axis = 'index')
            y = prem_ratio[select].mean()

        plt.plot(agerange, y, label = age)
        plt.legend(title = 'Issuance age')
        plt.ylabel('annual premium rate')
        plt.xlabel('insured age')
        plt.title(f'Premium ratio averaging method: {method}')
        # plt.close()

issuetime = datetime.datetime(1999, 1, 1, 0, 0)
seldate = abs(prem_tbl.PolicyDate - issuetime) < pd.Timedelta(365*3,'D')
prem_tbl_seldate = prem_tbl[seldate]
plotEmpPrembyMethod([40, 55, 70, 85], 'absolute', prem_tbl = prem_tbl_seldate)
plotEmpPrembyMethod([40, 55, 70, 85], 'FA-weighted', prem_tbl = prem_tbl_seldate)


    durange = range(40)
    plt.plot(durange, getAnnualYield(durange=durange, intertype='linear'))
    plt.plot(durange, getAnnualYield(durange=durange, intertype='quadratic'))
    ages = range(100)
    flatrates = [getFlatpr(
        isMale=True, age=age, r_free=fetchdata.getAnnualYield()
    ) for age in ages]
    plt.plot(ages, flatrates)
    
    ages = range(100)
    flatrates_svr = [getFlatpr(
        isMale=True, age=age, r_free=0.0375
    ) for age in ages]
    flatrates_stableyield = [getFlatpr(
        isMale=True, age=age, r_free=0.1
    ) for age in ages]
    flatrate_yc = [getFlatpr(
        isMale=True, age=age, r_free=fetchdata.getAnnualYield()
    ) for age in ages]

    plt.plot(ages, flatrates_svr, label='SVR, 0.0375')
    plt.plot(ages, flatrate_yc, c='red', label='YC')
    plt.plot(ages, flatrates_stableyield, c='green', label='stable 0.1')

    plt.legend()
    plt.show()

    age = 50
    plt.plot(getVariablePr(isMale=True, age=age))
    plt.axhline(y=flatrates[age], c='orange')
    plt.xlim(0, 99-age)
    plt.ylim(0, 0.99)

    print(f'age: {age}, rate: {flatrate}')
    risk-free rate
    rFree = 0.005
    age_v = 75
    pr_v = 0.002
    explore_plot(rFree=0.005, age_v=80, pr_v=0.002)
    explore_plot(rFree=0.01, age_v=75, pr_v=0.002)

    explore_plot(rFree=0.01, age_v=75, pr_v=0.05)
    explore_plot(rFree=0.01, age_v=75, pr_v=0.014)
    explore_plot(rFree=0.01, age_v=75, pr_v=0.009)


    explore_plot(rFree=0.01, age_v=55, pr_v=0.0001)

    explore_plot(rFree=0.07, age_v=85, pr_v=0.02)


    explore_plot(rFree=fetchdata.getAnnualYield(),
                 age_v=85, pr_v=flatrates[25])
