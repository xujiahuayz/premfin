import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from premiumFinance.constants import DATA_FOLDER


def get_hrs_data(table_name: str) -> pd.DataFrame:
    # Path to the .sas7bdat file
    file_path = DATA_FOLDER / f"HRS/h20core/h20sta/H20{table_name}.dta"
    return pd.read_stata(file_path)


# HRS 2020 Final Release: https://hrs.isr.umich.edu/sites/default/files/meta/2020/core/codebook/h20_00.html
# Wills and Life Insurance
hrs_mergede = get_hrs_data("T_R")
hrs_demographics = get_hrs_data("B_R")
hrs_assets = get_hrs_data("Q_H")
hrs_health = get_hrs_data("C_R")
hrs_person = get_hrs_data("PR_R")
hrs_job = get_hrs_data("M1_R")


id_cols = ["HHID", "PN"]

# merge tables on index and remove duplicate columns
hrs_merged = (
    hrs_mergede[
        id_cols
        + [
            "RT041",  # Was this lapse or cancellation something you chose to do, or was it done by the provider, your employer, or someone else?
            "RT042",  # Was it because the policy was too expensive, because you did not need the coverage or some other reason?
            "RT043",  # Did you receive any cash when the policy was cancelled or allowed to lapse? 1 yes, 5 no
        ]
    ]
    .merge(
        hrs_demographics[
            id_cols
            + [
                "RB014",  # What is the highest grade of school or year of college you completed?
            ]
        ],
        on=id_cols,
        how="outer",
    )
    .merge(
        hrs_assets[
            [
                "HHID",
                "RQ015",  # What was your income from self-employment, before taxes and other deductions
                "RQ020",  # About how much wage and salary income did you receive
                "RQ025",
                "RQ030",
                "RQ035",
            ]
        ],
        on="HHID",
        how="outer",
    )
    .merge(
        hrs_health[
            id_cols
            + [
                "RC001",  # RATE HEALTH, 1 excellent, 5 poor
            ]
        ],
        on=id_cols,
        how="outer",
    )
    .merge(
        hrs_person[
            id_cols
            + [
                "RX067_R",  # What year FNAME born
            ]
        ],
        on=id_cols,
        how="outer",
    )
    .merge(
        hrs_job[
            id_cols
            + [
                "RM002",  # Do you have any impairment or health problem that limits the kind or amount of paid work you can do? 1 yes, 5 no
            ]
        ]
    )
)


def plot_cross_distribution(col1: str, col2: str, df: pd.DataFrame) -> None:
    """Plot cross distribution of two columns in hrs_merged"""
    # get value counts of col1 and col2
    cross_dist = df[[col1, col2]].value_counts().sort_index()
    # filter with col1 = 1 or 5
    # cross_dist = cross_dist[cross_dist.index.get_level_values(0).isin([1, 5])]
    # get sum of col2 for each col1 and add the sum column to cross_dist
    sum_col = cross_dist.groupby(level=0).sum()
    # join two pandas series sum_col and cross_dist to form a dataframe
    cross_dist = cross_dist.to_frame().join(sum_col, lsuffix="", rsuffix="_sum")
    cross_dist["pdf"] = cross_dist["count"] / cross_dist["count_sum"]
    # cumsum of the count column by col1 and divide by the sum column
    cross_dist["cdf"] = (
        cross_dist["count"].groupby(level=0).cumsum() / cross_dist["count_sum"]
    )

    # plot pdfs in grouped bar chart with col2 as x-axis and col1 as hue
    # Reset the index to make plotting easier
    cross_dist = cross_dist.reset_index()

    # Create a grouped bar chart using seaborn
    plt.figure(figsize=(12, 6))
    sns.barplot(data=cross_dist, x=col2, y="pdf", hue=col1)

    # Customize the plot
    plt.xlabel(col2)
    plt.ylabel("pdf")
    plt.legend(title=col1)
    plt.show()


plot_cross_distribution(
    "RT041", "RC001", df=hrs_merged[hrs_merged["RT041"].isin([1, 2])]
)

plot_cross_distribution(
    "RT043", "RC001", df=hrs_merged[hrs_merged["RT043"].isin([1, 5])]
)

plot_cross_distribution(
    "RT043",
    "RM002",
    df=hrs_merged[hrs_merged["RT043"].isin([1, 5]) & hrs_merged["RM002"].isin([1, 5])],
)

plot_cross_distribution("RX067_R", "RC001", df=hrs_merged)

# sum hrs_merged["RQ020"] and hrs_merged["RQ015"], result only na if both are na, if only one is na, then replace that na with 0
hrs_merged["income"] = (
    hrs_merged["RQ020"].fillna(0)
    + hrs_merged["RQ015"].fillna(0)
    + hrs_merged["RQ025"].fillna(0)
    + hrs_merged["RQ030"].fillna(0)
    + hrs_merged["RQ035"].fillna(0)
)
# replace 0 with nan where  both hrs_merged["RQ020"] and hrs_merged["RQ015"] are na
hrs_merged["income"][
    hrs_merged["RQ020"].isna()
    & hrs_merged["RQ015"].isna()
    & hrs_merged["RQ025"].isna()
    & hrs_merged["RQ030"].isna()
    & hrs_merged["RQ035"].isna()
] = None


# calculate mean income by RT041
hrs_merged.groupby("RT041")["income"].mean()
hrs_merged.groupby("RT041")["income"].median()

hrs_merged.groupby("RT042")["income"].mean()
hrs_merged.groupby("RT042")["income"].median()

hrs_merged.groupby("RT043")["income"].mean()
hrs_merged.groupby("RT043")["income"].median()


# csv_health = hrs_merged[["RT043", "RC001"]].value_counts().sort_index()
# # filter with RT043 = 1 or 5
# csv_health = csv_health[csv_health.index.get_level_values(0).isin([1, 5])]
# # get sum of RC001 for each RT043 and add the sum column to csv_health
# sum_col = csv_health.groupby(level=0).sum()
# # join two pandas series sum_col and csv_health to form a dataframe
# csv_health = csv_health.to_frame().join(sum_col, lsuffix="", rsuffix="_sum")
# csv_health["pdf"] = csv_health["count"] / csv_health["count_sum"]
# # cumsum of the count column by RT043 and divide by the sum column
# csv_health["cdf"] = (
#     csv_health["count"].groupby(level=0).cumsum() / csv_health["count_sum"]
# )

# # plot pdfs in grouped bar chart with RC001 as x-axis and RT043 as hue
# # Reset the index to make plotting easier
# csv_health = csv_health.reset_index()

# # Create a grouped bar chart using seaborn
# plt.figure(figsize=(12, 6))
# sns.barplot(data=csv_health, x="RC001", y="pdf", hue="RT043")

# # Customize the plot
# plt.xlabel("RT001")
# plt.ylabel("pdf")
# plt.legend(title="RT043")
# plt.show()

# who_lapse = hrs_merged["RT041"].value_counts()
# # get value count where RT041 is 1.0
# self_or_else_lapse = who_lapse[1] + who_lapse[2]
# who_lapse[2] / self_or_else_lapse
# # 0.32682926829268294


# # Was it because the policy was too expensive, because you did not need the
# #          coverage or some other reason?
# why_lapse = hrs_merged["RT042"].value_counts()
# # add 1-9 of why_lapse
# reason_lapse = why_lapse[:9].sum()

# eligible_for_cash = (
#     why_lapse[1] + why_lapse[2] + why_lapse[3] + why_lapse[4] + why_lapse[7]
# )

# hrs_merged["RT042"].value_counts()
# 133 / eligible_for_cash

# why_lapse[4] / reason_lapse
# (
#     why_lapse[1] + why_lapse[2] + why_lapse[3] + why_lapse[4] + why_lapse[7]
# ) / reason_lapse
# why_lapse[7] / reason_lapse
