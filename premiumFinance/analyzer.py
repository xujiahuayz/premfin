from dataclasses import dataclass
import pandas as pd
import numpy as np
import constants
from os import path
import matplotlib.pyplot as plt
from scipy import optimize

from insured import Insured
from inspolicy import InsurancePolicy
from core import Mortality

insrdA = Insured(
    issueage=50,
    isMale=True,
    isSmoker=True,
    currentage=60,
    issuemort=0.9,
    currentmort=1.3,
)

insPol = InsurancePolicy(insrd=insrdA, lapse_assumption=False)
# insPol.__post_init__(r_free=0, pr=0.01)

insPol.getFlatpr()
insPol.getIRR()