import pandas as pd
from scipy import optimize

from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH
from premiumFinance.insured import Insured
from scripts.get_untappedprofit_policyholder import policyholder_policy_value


def find_breakeven_mortality(
    issue_age: float,
    is_male: bool,
    is_smoker: bool,
    current_age: float,
    current_vbt: str = "VBT15",
) -> tuple[float, float]:
    """
    find out breakeven mortality rate for each insured cohort
    and the corresponding life expectancy
    """
    try:
        result = optimize.root_scalar(
            lambda r: policyholder_policy_value(
                issue_age=issue_age,
                is_male=is_male,
                is_smoker=is_smoker,
                current_age=current_age,
                current_vbt=current_vbt,
                current_mort=r,
            ),
            bracket=[0.001, 1.9],
            method="brentq",
        ).root
    except ValueError:
        result = 0.0001

    this_insured = Insured(
        issue_age=issue_age,
        is_male=is_male,
        is_smoker=is_smoker,
        current_age=current_age,
        issue_vbt="VBT01",
        current_vbt=current_vbt,
        current_mort=result,
    )
    print(result)
    return result, this_insured.mortality_now.life_expectancy + current_age


if __name__ == "__main__":
    mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

    mortality_experience[
        ["breakeven_mortality", "breakeven"]
    ] = mortality_experience.apply(
        lambda row: find_breakeven_mortality(
            issue_age=row["issueage"],
            is_male=row["isMale"],
            is_smoker=row["isSmoker"],
            current_age=row["currentage"],
            current_vbt="VBT15",
        ),
        axis=1,
        result_type="expand",
    )
    mortality_experience.to_excel(MORTALITY_TABLE_CLEANED_PATH, index=False)
