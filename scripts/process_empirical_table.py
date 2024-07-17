import numpy as np
import re
import pandas as pd
from premiumFinance.constants import DATA_FOLDER, MORTALITY_TABLE_CLEANED_PATH


def get_representative_age(x: str) -> int:
    return int(np.mean([int(x) for x in re.split("[+-]", x) if x != ""]))


# %% prepare datatable
if __name__ == "__main__":
    mortality_experience_path = DATA_FOLDER / "mortalityexperience.xlsx"

    mortality_experience = pd.read_excel(mortality_experience_path, engine='openpyxl')


    mortality_experience["issueage"] = mortality_experience["Issue Age Group"].map(
        get_representative_age
    )
    mortality_experience["currentage"] = mortality_experience["Attained Age Group"].map(
        get_representative_age
    )
    mortality_experience["isMale"] = mortality_experience["Gender"].map(
        lambda x: True if x == "Male" else False
    )
    mortality_experience["isSmoker"] = mortality_experience["Smoker Status"].map(
        lambda x: {"NonSmoker": False, "Smoker": True, "Unknown": None}[x]
    )

    mortality_experience.rename(
        columns={
            "Amount Exposed ": "Amount Exposed",
            "Policies Exposed ": "Policies Exposed",
        },
        inplace=True,
    )

    mortality_experience_clean = mortality_experience[
        [
            "Issue Age Group",
            "Attained Age Group",
            "issueage",
            "currentage",
            "isMale",
            "isSmoker",
            "Amount Exposed",
            "Policies Exposed",
        ]
    ]
    # mortality_experience_clean["Amount Exposed"] = mortality_experience["Amount Exposed "]
    # mortality_experience_clean["Policies Exposed"] = mortality_experience[
    #     "Policies Exposed "
    # ]
    mortality_experience_clean.to_excel(MORTALITY_TABLE_CLEANED_PATH, index=False)

# %%
