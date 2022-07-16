from dataclasses import dataclass
from typing import Optional

from premiumFinance.mortality import Mortality


@dataclass
class Insured:
    issue_age: int
    current_age: Optional[int]
    is_male: bool = True
    is_smoker: Optional[bool] = False
    issue_mort: float = 1
    current_mort: float = 1
    issue_vbt: str = "VBT01"
    current_vbt: str = "VBT15"

    def __post_init__(self):
        if self.current_age is None:
            self.current_age = self.issue_age
        assert (
            self.issue_age <= self.current_age
        ), "Issue age must not exceed current age"

    @property
    def mortality_at_issue(self):
        im = Mortality(
            issue_age=self.issue_age,
            current_age=self.issue_age,  # currentage = issueage at policy issuance
            is_male=self.is_male,
            is_smoker=self.is_smoker,
            mort_rate=self.issue_mort,
            which_vbt=self.issue_vbt,
        )
        return im

    @property
    def mortality_now(self):
        cm = Mortality(
            issue_age=self.issue_age,
            current_age=self.current_age,
            is_male=self.is_male,
            is_smoker=self.is_smoker,
            mort_rate=self.current_mort,
            which_vbt=self.current_vbt,
        )
        return cm
