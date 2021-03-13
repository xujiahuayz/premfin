import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot as plt
from scipy import optimize

from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.core import Mortality
from premiumFinance.fetchdata import getAnnualYield

insrd_benchmark = Insured(
    issueage=40,
    isMale=True,
    isSmoker=False,
    currentage=70,
    issuemort=0.95,
    currentmort=1.2,
)

insrd_fem = Insured(
    issueage=40,
    isMale=False,
    isSmoker=True,
    currentage=70,
    issuemort=0.95,
    currentmort=1.2,
)

insrd_smoker = Insured(
    issueage=40,
    isMale=True,
    isSmoker=True,
    currentage=70,
    issuemort=0.95,
    currentmort=1.2,
)


insrd_oldissueage = Insured(
    issueage=60,
    isMale=True,
    isSmoker=False,
    currentage=70,
    issuemort=0.95,
    currentmort=1.2,
)


insrd_oldcurrentage = Insured(
    issueage=40,
    isMale=True,
    isSmoker=False,
    currentage=90,
    issuemort=0.95,
    currentmort=1.2,
)

insrd_sickissue = Insured(
    issueage=40,
    isMale=True,
    isSmoker=False,
    currentage=70,
    issuemort=1.3,
    currentmort=1.2,
)

insrd_sickcurrent = Insured(
    issueage=40,
    isMale=True,
    isSmoker=False,
    currentage=70,
    issuemort=0.95,
    currentmort=1.5,
)

insPol1 = InsurancePolicy(insrd=insrd_benchmark, lapse_assumption=False, r_free=0.001)
insPol2 = InsurancePolicy(
    insrd=insrd_benchmark, lapse_assumption=False, r_free=getAnnualYield()
)
insPol3 = InsurancePolicy(
    insrd=insrd_benchmark, lapse_assumption=True, r_free=getAnnualYield()
)
# insPol1.plotPersRate()
# insPol3.plotPersRate()
insPol3.plotPersRate(atIssue=False)