from dataclasses import dataclass
import pandas as pd
import numpy as np
import constants
from os import path
import matplotlib.pyplot as plt

from insured import Insured

pers_file = path.join(constants.DATA_FOLDER, "persistency.xlsx")
tbl = pd.read_excel(
    pers_file,
    sheet_name="Universal Life",
    index_col=0,
    skiprows=8,
    skipfooter=71,
    usecols="J:K,O",
)


@dataclass
class InsurancePolicy:
    insrd: Insured
    lapse_assumption: bool = True
    # spread

    # def __post_init__(self,spread):

    def lapseRate(self, doplot=False):
        if self.lapse_assumption:
            col_ind = 0 if self.insrd.isMale else 1
            lapse_rate = pd.Series([0]).append(
                tbl.iloc[:, col_ind] / 100, ignore_index=True
            )
        else:
            lapse_rate = [0]
        if doplot:
            plt.plot(lapse_rate)
        return lapse_rate

    def condPersRate(self, doplot=False):
        condSurv = self.insrd.indiMort().condSurvCurv()
        lapse_rate = self.lapseRate()

        n = len(lapse_rate)
        persrate = []
        i = 0
        for w in condSurv:
            if i < n:
                lapserate = 1 - lapse_rate[i]
                i += 1
            rate = w * lapserate
            persrate.append(rate)

        if doplot:
            plt.plot(persrate)
        return persrate

    def persRate(self):
        persrate = self.condPersRate()
        pers = np.cumprod(persrate)
        return pers

    def plotPersRate(self):
        self.insrd.indiMort().plotSurvCurv()
        pers = self.persRate()
        plt.plot(np.arange(len(pers)) + self.insrd.currentage, pers)