import pandas as pd
from premiumFinance.constants import DATA_FOLDER


def get_hrs_data(table_name: str) -> pd.DataFrame:
    # Path to the .sas7bdat file
    file_path = DATA_FOLDER / f"HRS/h20core/h20sta/H20{table_name}.dta"
    return pd.read_stata(file_path)


# HRS 2020 Final Release: https://hrs.isr.umich.edu/sites/default/files/meta/2020/core/codebook/h20_00.html
# Wills and Life Insurance
hrs_life_insur = get_hrs_data("T_R")
hrs_demographics = get_hrs_data("B_R")


# number of rows
hrs_life_insur.shape[0]

# count of different values in a column "RT040"
# https://hrs.isr.umich.edu/sites/default/files/meta/2020/core/codebook/h20t_ri.htm
hrs_life_insur["RT040"].value_counts()


# RT041 Was this lapse or cancellation something you chose to do, or was it done by the
#          provider, your employer, or someone else?
who_lapse = hrs_life_insur["RT041"].value_counts()
# get value count where RT041 is 1.0
self_or_else_lapse = who_lapse[1] + who_lapse[2]
who_lapse[2] / self_or_else_lapse
# 0.32682926829268294

# Was it because the policy was too expensive, because you did not need the
#          coverage or some other reason?
why_lapse = hrs_life_insur["RT042"].value_counts()
# add 1-9 of why_lapse
reason_lapse = why_lapse[:9].sum()

eligible_for_cash = (
    why_lapse[1] + why_lapse[2] + why_lapse[3] + why_lapse[4] + why_lapse[7]
)

hrs_life_insur["RT042"].value_counts()
133 / eligible_for_cash

why_lapse[4] / reason_lapse
(
    why_lapse[1] + why_lapse[2] + why_lapse[3] + why_lapse[4] + why_lapse[7]
) / reason_lapse
why_lapse[7] / reason_lapse
