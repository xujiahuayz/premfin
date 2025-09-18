"""
define Insured class and its methods
"""

from dataclasses import dataclass

from premiumFinance.mortality import Mortality


@dataclass
class Insured:
    """
    insured of a life policy
    """

    issue_age: float
    current_age: float
    is_male: bool = True
    is_smoker: bool | None = False
    issue_mortality_factor: float = 1
    current_mortality_factor: float = 1
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
        """
        mortality profile at policy issuance
        """
        return Mortality(
            issue_age=self.issue_age,
            current_age=self.issue_age,  # current_age = issue_age at policy issuance
            is_male=self.is_male,
            is_smoker=self.is_smoker,
            mort_rate=self.issue_mortality_factor,
            which_vbt=self.issue_vbt,
        )

    @property
    def mortality_now(self):
        """
        mortality profile now
        """
        return Mortality(
            issue_age=self.issue_age,
            current_age=self.current_age,
            is_male=self.is_male,
            is_smoker=self.is_smoker,
            mort_rate=self.current_mortality_factor,
            which_vbt=self.current_vbt,
        )
