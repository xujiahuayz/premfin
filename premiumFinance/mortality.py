from dataclasses import dataclass
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

from premiumFinance.fetchdata import get_vbt_data

EPSILON = 1e-10


@dataclass
class Mortality:
    """
    characterize an insured's mortality profile
    """

    issue_age: float
    current_age: float
    is_male: bool
    is_smoker: Optional[bool] = None
    mort_rate: float = 1
    which_vbt: str = "VBT01"

    def __post_init__(self):
        assert (
            self.issue_age <= self.current_age
        ), "Issue age must not exceed current age"

    @property
    def gender(self) -> str:
        mf = "Male" if self.is_male else "Female"
        return mf

    @property
    def basemort_curv(self) -> pd.Series:
        mort = get_vbt_data(
            vbt=self.which_vbt,
            is_male=self.is_male,
            is_smoker=self.is_smoker,
            issue_age=self.issue_age,
            current_age=self.current_age,
        )
        return mort

    @property
    def conditional_mortality_curve(self) -> pd.Series:
        mort = self.basemort_curv
        # adjust mortality rate with multiplier
        cond_mort = pd.Series(min(1 - EPSILON, self.mort_rate * q) for q in mort)
        return cond_mort

    @property
    def conditional_survival_curve(self) -> pd.Series:
        cond_mort = self.conditional_mortality_curve
        cond_surv = 1 - cond_mort
        return cond_surv

    @property
    def surv_curv(self) -> np.ndarray:
        condSurv = self.conditional_survival_curve
        surv = np.cumprod(condSurv)
        return surv

    @property
    def life_expectancy(self) -> float:
        surv = self.surv_curv
        le = np.sum(surv) - 0.5
        return le

    def plot_surv_curv(self):
        surv = self.surv_curv
        le = self.life_expectancy
        leage = le + self.current_age
        plt.plot(surv.index + self.current_age, surv, label="Survival rate")
        plt.xlabel("Age")
        plt.ylabel("Cumulative probability")
        plt.axvline(leage, color="red", label=f"LE: {round(leage,1)}")
        plt.title(
            f"issue age: {self.issue_age}, gender: {self.gender}, smoker: {self.is_smoker}"
        )
        plt.axvline(self.current_age, ls="--", lw=0.5, color="gray")
        plt.axhline(0, ls="--", lw=0.5, color="gray")
        plt.axhline(1, ls="--", lw=0.5, color="gray")
        plt.legend()
