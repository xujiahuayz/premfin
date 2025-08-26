# process a large dataset from DATA_FOLDER/SOA/ILEC_2012_19 - 20240429.txt with over 50 million rows

from matplotlib.axes import Axes
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from premiumFinance.constants import DATA_FOLDER
mortality_data = pd.read_pickle(DATA_FOLDER / "SOA" / "mortality_data.pkl")

mortality_data["Type"] = mortality_data["Insurance_Plan"].apply(
    lambda x: 'Whole' if x =='Perm' else (x if x in ["Term", "Other"] else "Universal"))
    # lambda x: x if x in ["Term", 'Perm', "Other"] else "Perm")


POLICY_TYPES_ORDER = ['Whole', 'Universal', 'Term', 'Other']
# mortality_data_selected = mortality_data[[
#     "Observation_Year", "Age_Ind", "Sex", "Smoker_Status", 'Insurance_Plan', 'Issue_Age', 'Issue_Year', 'Attained_Age',
#     'Amount_Exposed', 'Policies_Exposed', 'Average_Face_Amount'
# ]]

# compute sum of Amount_Exposed and Policies_Exposed, grouped by Observation_Year and Insurance_Plan

YEAR_TYPE = 'Observation_Year'
# if we use 'Issue_Year' instead, we'll see that permanent + universal life insurance accounts for ~20% of the total amount, consistent with ACLI

mortality_data_selected = mortality_data.groupby([YEAR_TYPE, "Type"]).agg({
    "Amount_Exposed": "sum",
    "Policies_Exposed": "sum",
}).reset_index()

# calculate Percentage of Amount_Exposed and Policies_Exposed for each Type within each Observation_Year
mortality_data_selected["Percentage_Amount_Exposed"] = (
    mortality_data_selected.groupby(YEAR_TYPE)["Amount_Exposed"]
    .transform(lambda x: (x / x.sum()) * 100)
)
mortality_data_selected["Percentage_Policies_Exposed"] = (
    mortality_data_selected.groupby(YEAR_TYPE)["Policies_Exposed"]
    .transform(lambda x: (x / x.sum()) * 100)
)

# create a new column for Type based on Insurance_Plan, where "Term" and "Other" are kept, everything else is "Perm"
def plot_stacked_bars(
    axis: Axes,
    data: pd.DataFrame,
    years: np.ndarray,
    x_coords: np.ndarray,
    offset: float,
    bar_label: str,
    scale: float,
    year_col_name: str = YEAR_TYPE,
    value_col_name: str = "Amount_Exposed",
    percentage_col_name: str = "Percentage_Amount_Exposed",
    annotated_type: list[str] = ["Whole", 'Universal', 'Term'],
    colors: list[str] = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728'],
    policy_type: list[str] = POLICY_TYPES_ORDER,
    width: float = 0.35,
) -> None:
    """
    Draws a single stacked bar on a given axis and adds percentage labels
    for the 'ordinary life' category.
    """
    bottom = np.zeros(len(years))
    
    for i, p_type in enumerate(policy_type):
        # Filter for the specific policy type and align with years
        type_data = data[data["Type"] == p_type].set_index(year_col_name).reindex(years).fillna(0)

    
        values = type_data[value_col_name] / scale

        axis.bar(
            x_coords + offset,
            values,
            width,
            label=p_type,
            bottom=bottom,
            color=colors[i],
            alpha=0.8,
        )
        
        # --- Add Percentage Label for 'ordinary life' ---
        if p_type in annotated_type:
            percentages = type_data[percentage_col_name]
            # Iterate through each bar to place the text
            for idx, percentage in enumerate(percentages):
                # Y position is in the middle of the 'ordinary life' segment
                axis.text(
                    x_coords[idx] + offset,
                    bottom[idx] + (values.iloc[idx] / 2),
                    f"({percentage:.0f}%)", # Format as integer percentage
                    ha='center',
                    va='center',
                    fontsize=8,
                )

                # axis.text(
                #     x=x_coords[idx] + offset,
                #     y=bottom[idx] + values.iloc[idx], # Position at the top of the segment
                #     s=round(values.iloc[idx]),
                #     ha='center',
                #     va='top', # Align bottom of text with the y-coordinate
                #     fontsize=9,
                # )
        
                # add text for total value at the top of each bar
        # print(values.values)
        bottom += values.values

    # for x, y in zip(x_coords, bottom):

    #     axis.text(
    #                     x=x + offset,
    #                     y=y, # Position at the top of the segment
    #                     s=round(y),
    #                     ha='center',
    #                     va='bottom', # Align bottom of text with the y-coordinate
    #                     fontsize=10,
    #                     fontweight='bold',
    #                 )
    
    # Format the axis
    axis.set_ylabel(bar_label, weight='bold', fontsize=12)



    # YEARS = sorted(num_plot_data["Year"].unique())
    # x = np.arange(len(YEARS))  # the label locations
    # bar_width = 0.35  # the width of each bar group

    # fig, ax1 = plt.subplots(figsize=(18, 10))
    # ax2 = ax1.twinx()  # Create a second y-axis sharing the x-axis

    # # 5. Plot the Data
    # # Plot 'Number of Policies' on the primary axis (ax1)
    # plot_stacked_bars(
    #     axis=ax1,
    #     data=num_plot_data,
    #     years=YEARS,
    #     x_coords=x,
    #     offset=-bar_width / 1.7,
    #     bar_label="Number of Policies (in millions)",
    #     scale=1e6, # Values are in single units, scale to millions
    #     width=bar_width
    # )

# only look at year after 2015
# mortality_data_selected = mortality_data_selected[mortality_data_selected[YEAR_TYPE] >= 2015]

YEARS = sorted(mortality_data_selected[YEAR_TYPE].unique())
x = np.arange(len(YEARS))  # the label locations
bar_width = 0.35  # the width of each bar group
fig, ax1 = plt.subplots(figsize=(18, 10))
ax2 = ax1.twinx()  # Create a second y-axis sharing the x

plot_stacked_bars(
    axis=ax1,
    data=mortality_data_selected,
    years=YEARS,
    x_coords=x,
    offset=-bar_width / 1.7,
    bar_label="Policies Exposed (in millions)",
    scale=1e6,  # Values are in single units, scale to millions
    year_col_name=YEAR_TYPE,
    value_col_name="Policies_Exposed",
    percentage_col_name="Percentage_Policies_Exposed",
)

plot_stacked_bars(
    axis=ax2,
    data=mortality_data_selected,
    years=YEARS,
    x_coords=x,
    offset=bar_width / 2,
    bar_label="Amount Exposed (in trillions)",
    scale=1e12,  # Values are in single units, scale to millions
    year_col_name=YEAR_TYPE,
    value_col_name="Amount_Exposed",
    percentage_col_name="Percentage_Amount_Exposed",
)

ax1.set_xticks(x)
ax1.set_xticklabels(YEARS)
handles, labels = ax1.get_legend_handles_labels()
    # Since we use a defined order, we can map labels to handles safely
unique_labels = dict(zip(labels, handles))
fig.legend(
        unique_labels.values(),
        unique_labels.keys(),
        title="Policy Type",
        ncol=len(POLICY_TYPES_ORDER),
        loc="upper center",
        fontsize=12,
        title_fontsize=13
    )    
