from dataclasses import dataclass
from typing import Optional

from premiumFinance.mortality import Mortality


@dataclass
class Insured:
    issue_age: int
    current_age: Optional[int]
    isMale: bool = True
    isSmoker: Optional[bool] = False
    issuemort: float = 1
    currentmort: float = 1
    issueVBT: str = "VBT01"
    currentVBT: str = "VBT15"

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
            is_male=self.isMale,
            is_smoker=self.isSmoker,
            mort_rate=self.issuemort,
            which_vbt=self.issueVBT,
        )
        return im

    @property
    def mortality_now(self):
        cm = Mortality(
            issue_age=self.issue_age,
            current_age=self.current_age,
            is_male=self.isMale,
            is_smoker=self.isSmoker,
            mort_rate=self.currentmort,
            which_vbt=self.currentVBT,
        )
        return cm
