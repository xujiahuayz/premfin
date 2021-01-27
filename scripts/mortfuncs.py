from pandas import read_excel, Series
from numpy import cumprod
from pickle import load
from CONST import *

vbt = load(open(DATA_FOLDER + 'vbt', 'rb'))

# need to `pip install openpyxl`
malevbt = read_excel(
    vbt, sheet_name='2015 Male Unismoke ANB', header=2, index_col=0
)
femavbt = read_excel(
    vbt, sheet_name='2015 Female Unismoke ANB', header=2, index_col=0
)


# survival curve
def getSurcurv(isMale: bool, age: int, mortrate=1):
    tbl = malevbt if isMale else femavbt
    maxage = max(tbl.index)
    if age <= maxage:
        curv = tbl.loc[age][:25].append(tbl['Ult.'][age:])
    else:
        curv = tbl.loc[maxage][(age-maxage):26]
    mort = Series([0]).append(curv, ignore_index=True)
    surv = cumprod(1-mort/1000)
    return surv


# `pr` is premium rate: premium / deth benefit
def getPV_pr(pr, surv=None, isMale=None, age=None, r_free: float = 0.1) -> float:
    if surv is None:
        surv = surcurv(isMale, age)

    cf = 0
    if isinstance(pr, (int, float)):
        # assert pr < 1, 'premium rate must be below 1'
        for i in surv.index:
            cf += surv[i] / (1+r_free)**i
        cf *= pr

    else:
        assert len(surv) == len(
            pr), 'survial curve and premium curve must have the same length'
        # assert all(p < 1 for p in pr), 'premium rates must be all below 1'
        for i in surv.index:
            cf += (surv[i] * pr[i]) / (1+r_free)**i

    return cf


def getPV_db(surv=None, isMale=None, age=None, r_free: float = 0.1) -> float:
    if surv is None:
        surv = surcurv(isMale, age)

    cf = 0
    oneperiod_mort = -surv.diff()[1:]
    for i in oneperiod_mort.index:
        cf += oneperiod_mort[i] / (1+r_free)**i
    return cf


def getPV_endpay(pr, surv=None, isMale=None, age=None, r_b: float = 0.2, r_free: float = 0.1) -> float:
    if surv is None:
        surv = surcurv(isMale, age)

    cf = 0
    oneperiod_mort = -surv.diff()[1:]

    for i in oneperiod_mort.index:
        debt = 0

        if isinstance(pr, (int, float)):
            for j in range(i):
                debt += (1+r_b)**(i-j)
            debt *= pr
        else:
            assert len(surv) == len(
                pr), 'survial curve and premium curve must have the same length'
            for j in range(i):
                debt += pr[j] * (1+r_b)**(i-j)

        cf += oneperiod_mort[i] * debt / (1+r_free)**i

    return cf


def getPV_agents(finop: str, pv_db_value=None, pv_pr_value=None, pv_debt_value=None, tp=None):
    assert finop in FIN_OPTIONS, '`finot` must be one of ' + str(FIN_OPTIONS)

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
