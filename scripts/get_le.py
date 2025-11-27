import pandas as pd

from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH
from premiumFinance.mortality import Mortality

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

# calculate life expectancy for each row, where each row describes a Mortality object
mortality_experience["life_expectancy"] = mortality_experience.apply(
    lambda row: Mortality(
        issue_age=row["issueage"],
        current_age=row["currentage"],
        is_male=row["isMale"],
        is_smoker=row["isSmoker"],
        mort_rate=1,
        which_vbt="VBT15",
    ).life_expectancy,
    axis=1,
)

# save back to the same file
mortality_experience.to_excel(MORTALITY_TABLE_CLEANED_PATH, index=False)
