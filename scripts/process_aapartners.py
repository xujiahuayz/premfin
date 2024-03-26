import pandas as pd
import numpy as np
from premiumFinance.constants import DATA_FOLDER, MORTALITY_TABLE_CLEANED_PATH
from scripts.process_mortality_table import mortality_experience

AAPARTNERS_PATH = DATA_FOLDER / "2016 Medical Underwriting final.xlsx"
AAPARTNERS_SHEET = "Full Sample"

# get dataframe from MORALITY_TABLE_CLEANED_PATH

# mortality_experience = pd.read_excel(
#     MORTALITY_TABLE_CLEANED_PATH,
#     engine="openpyxl",
# )

# # get the start of issue_age_group by getting 2 digits from the start of the string
# mortality_experience["issue_age_group_start"] = (
#     mortality_experience["Issue Age Group"].str.extract(r"(\d{2})").astype(int)
# )
# issue_age_group_start = mortality_experience["issue_age_group_start"].unique()

# mortality_experience["attained_age_group_start"] = (
#     mortality_experience["Attained Age Group"].str.extract(r"(\d{2})").astype(int)
# )
# attained_age_group_start = mortality_experience["attained_age_group_start"].unique()

# read "Full Sample" tab from "2016 Medical Underwriting final.xlsx" from DATA_FOLDER, A:S
aapartners = pd.read_excel(
    AAPARTNERS_PATH,
    sheet_name=AAPARTNERS_SHEET,
    engine="openpyxl",
    usecols="A:S",
)

# # get issueage from IssDate and Birthday, get exact number of days from IssDate and Birthday

# aapartners["issueage"] = (
#     aapartners["IssDate"] - aapartners["Birthday"]
# ).dt.days / 365.2425

# aapartners["issue_age_group_start"] = pd.cut(
#     aapartners["issueage"],
#     bins=np.append(issue_age_group_start, 999),
#     labels=issue_age_group_start,
#     right=False,
# ).astype(
#     float
# )  # type: ignore

# aapartners["attained_age_group_start"] = pd.cut(
#     aapartners["Age"],
#     bins=np.append(attained_age_group_start, 999),
#     labels=attained_age_group_start,
#     right=False,
# ).astype(
#     float
# )  # type: ignore


# aapartners["isSmoker"] = aapartners["Smoker"].map(lambda x: {"NS": 0.0, "S": 1}[x])
# # get isMale, {"M": True, "F": False}, use None for all other values
aapartners["isMale"] = aapartners["Gender"].map(
    lambda x: {"M": True, "F": False}.get(x, None)
)

# aapartners["age_diff"] = (
#     aapartners["attained_age_group_start"] - aapartners["issue_age_group_start"]
# )

# group by issue_age_group_start, attained_age_group_start, isMale, isSmoker, and sum "TP" and "FA"
aapartners_grouped = aapartners.groupby(
    [
        "isMale",
        # "isSmoker",
        # "age_diff",
        # "issue_age_group_start",
        # "attained_age_group_start",
    ]
)[["TP", "FA"]].sum()

aapartners_grouped["tp_rate"] = aapartners_grouped["TP"] / aapartners_grouped["FA"]

# mortality_experience["age_diff"] = (
#     mortality_experience["attained_age_group_start"]
#     - mortality_experience["issue_age_group_start"]
# )
