import pandas as pd
import numpy as np
import pickle
from constants import FIN_OPTIONS, DATA_FOLDER
from scipy import optimize
import fetchdata
import matplotlib.pyplot as plt


vbt = pickle.load(open(DATA_FOLDER + "vbt", "rb"))

# need to `pip install openpyxl`
malevbt = pd.read_excel(vbt, sheet_name="2015 Male Unismoke ANB", header=2, index_col=0)
femavbt = pd.read_excel(
    vbt, sheet_name="2015 Female Unismoke ANB", header=2, index_col=0
)


# conditional 1-period mortality curve
def getCondMortCurv(isMale: bool, age: int, mortrate=1):
    tbl = malevbt if isMale else femavbt
    maxage = max(tbl.index)
    if age <= maxage:
        curv = tbl.loc[age][:25].append(tbl["Ult."][age:])
    else:
        curv = tbl.loc[maxage][(age - maxage) : 26]
    mort = pd.Series([0]).append(curv / 1000, ignore_index=True)

    # adjust mortality rate with multiplier
    condMort = pd.Series(min(1, mortrate * q) for q in mort)
    return condMort


def getCondSurvCurv(isMale: bool, age: int, mortrate=1):
    condMort = getCondMortCurv(isMale, age, mortrate)
    condSurv = 1 - condMort
    return condSurv


# survival curve
def getSurcurv(isMale: bool, age: int, mortrate=1):
    condSurv = getCondSurvCurv(isMale, age, mortrate)
    surv = np.cumprod(condSurv)
    return surv


def getVariablePr(isMale: bool, age: int, mortrate=1, spread=0):
    condMort = getCondMortCurv(isMale, age, mortrate)
    condSurv = 1 - condMort
    breakevenPr = condMort / condSurv
    pr = breakevenPr + spread
    return pr


# `pr` is premium rate: premium / deth benefit
def getPV_pr(pr, surv=None, isMale=None, age=None, mortrate=1, r_free=0.005) -> float:

    if surv is None:
        surv = getSurcurv(isMale, age, mortrate)

    if isinstance(r_free, (int, float)):
        r_free = [r_free] * len(surv)

    cf = 0
    if isinstance(pr, (int, float)):
        # assert pr < 1, 'premium rate must be below 1'
        for i in surv.index:
            cf += surv[i] / (1 + r_free[i]) ** i
        cf *= pr

    else:
        assert len(surv) == len(
            pr
        ), "survial curve and premium curve must have the same length"
        # assert all(p < 1 for p in pr), 'premium rates must be all below 1'
        for i in surv.index:
            cf += (surv[i] * pr[i]) / (1 + r_free[i]) ** i

    return cf


def getPV_db(surv=None, isMale=None, age=None, mortrate=1, r_free=0.005) -> float:
    if surv is None:
        surv = getSurcurv(isMale, age, mortrate)

    if isinstance(r_free, (int, float)):
        r_free = [r_free] * len(surv)

    cf = 0
    oneperiod_mort = -surv.diff()[1:]
    for i in oneperiod_mort.index:
        cf += oneperiod_mort[i] / (1 + r_free[i]) ** i
    return cf


def insurerProfit(pr, surv=None, isMale=None, age=None, mortrate=1, r_free=0.005):
    PVdb = getPV_db(surv=surv, isMale=isMale, age=age, mortrate=mortrate, r_free=r_free)
    PVpr = getPV_pr(
        pr, surv=surv, isMale=isMale, age=age, mortrate=mortrate, r_free=r_free
    )
    pft = PVpr - PVdb
    return pft


def getFlatpr(surv=None, isMale=None, age=None, mortrate=1, r_free=0.005):
    sol = optimize.root_scalar(
        lambda pr: insurerProfit(pr, surv, isMale, age, mortrate, r_free),
        x0=0.004,
        bracket=[0, 1],
        method="brentq",
    )
    return sol.root


def getIRR(
    enterage,
    surv=None,
    isMale=None,
    age=None,
    mortrate=1,
    r_free=fetchdata.getAnnualYield(),
):
    breakEvenFlatpr = getFlatpr(
        surv=surv, isMale=isMale, age=enterage, mortrate=mortrate, r_free=r_free
    )
    sol = optimize.root_scalar(
        lambda r: insurerProfit(
            pr=breakEvenFlatpr,
            surv=surv,
            isMale=isMale,
            age=age,
            mortrate=mortrate,
            r_free=r,
        ),
        x0=0.0001,
        bracket=[0, 0.99],
        method="brentq",
    )
    return sol.root


def getEquivYield(
    surv=None,
    isMale=None,
    age=None,
    mortrate=1,
    r_free=fetchdata.getAnnualYield(),
    doplot: bool = False,
):
    breakEvenFlatpr = getFlatpr(
        surv=surv, isMale=isMale, age=age, mortrate=mortrate, r_free=r_free
    )
    sol = optimize.root_scalar(
        lambda r: insurerProfit(
            pr=breakEvenFlatpr,
            surv=surv,
            isMale=isMale,
            age=age,
            mortrate=mortrate,
            r_free=r,
        ),
        x0=0.0001,
        bracket=[0, 0.99],
        method="brentq",
    )

    if doplot:
        rs = np.arange(0, 0.5, 0.01)
        plt.plot(
            rs,
            [
                insurerProfit(
                    pr=breakEvenFlatpr,
                    surv=surv,
                    isMale=isMale,
                    age=age,
                    mortrate=mortrate,
                    r_free=r,
                )
                for r in rs
            ],
        )
        plt.show()
    return sol.root


def getPV_endpay(
    pr, surv=None, isMale=None, age=None, mortrate=1, r_b: float = 0.2, r_free=0.005
) -> float:
    if surv is None:
        surv = getSurcurv(isMale, age, mortrate)

    if isinstance(r_free, (int, float)):
        r_free = [r_free] * len(surv)

    cf = 0
    oneperiod_mort = -surv.diff()[1:]

    for i in oneperiod_mort.index:
        debt = 0

        if isinstance(pr, (int, float)):
            for j in range(i):
                debt += (1 + r_b) ** (i - j)
            debt *= pr
        else:
            assert len(surv) == len(
                pr
            ), "survial curve and premium curve must have the same length"
            for j in range(i):
                debt += pr[j] * (1 + r_b) ** (i - j)

        cf += oneperiod_mort[i] * debt / (1 + r_free[i]) ** i

    return cf


def getPV_agents(
    finop: str, pv_db_value=None, pv_pr_value=None, pv_debt_value=None, tp=None
):
    assert finop in FIN_OPTIONS, "`finot` must be one of " + str(FIN_OPTIONS)

    # case `lapse`
    if finop == FIN_OPTIONS[0]:
        financ = 0
        polhol = 0

    # case `nonrecourse`
    if finop == FIN_OPTIONS[1]:
        financ = min(pv_db_value, pv_debt_value) - pv_pr_value
        polhol = max(0, pv_db_value - pv_debt_value)

    # case `full recourse`
    if finop == FIN_OPTIONS[2]:
        financ = pv_debt_value - pv_pr_value
        polhol = pv_db_value - pv_debt_value

    # case `sale`
    if finop == FIN_OPTIONS[3]:
        financ = pv_db_value - pv_pr_value - tp
        polhol = tp

    return financ, polhol


if __name__ == "__main__":
    ages = range(100)
    flatrates_svr = [getFlatpr(isMale=True, age=age, r_free=0.0375) for age in ages]
    flatrates_stableyield = [
        getFlatpr(isMale=True, age=age, r_free=0.1) for age in ages
    ]
    flatrate_yc = [
        getFlatpr(isMale=True, age=age, r_free=fetchdata.getAnnualYield())
        for age in ages
    ]

    plt.plot(ages, flatrates_svr, label="SVR, 0.0375")
    plt.plot(ages, flatrate_yc, c="red", label="YC")
    plt.plot(ages, flatrates_stableyield, c="green", label="stable 0.1")

    plt.legend()
    plt.show()

    age = 50
    plt.plot(getVariablePr(isMale=True, age=age))
    plt.axhline(y=flatrates[age], c="orange")
    # plt.xlim(0, 99-age)
    # plt.ylim(0, 0.99)

    # print(f'age: {age}, rate: {flatrate}')
