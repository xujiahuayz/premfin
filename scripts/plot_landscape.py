# --- Imports ---
from __future__ import \
    annotations  # For postponed evaluation of type annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from premiumFinance.constants import DATA_FOLDER

EXCEL_PATH: Path = DATA_FOLDER / "SP" / "Exhibit of Life Insurance.xlsx"

# Configuration for different policy types
# Format: (sheet_base_name, type_label, num_policy_rows, amount_insurance_rows)
POLICY_CONFIGS: list[tuple[str, str, list[int], list[int]]] = [
    ("Indl Life", "industrial life", [15, 16, 22], [16, 17, 24]),
    ("Ordinary", "ordinary life", [15, 16, 22], [16, 17, 24]),
    ("Crdt Life", "credit life", [15, 16, 22], [16, 17, 24]),
    ("Group", "group life", [12, 13, 18], [16, 17, 23]),
]

# Define the order and colors for plotting to ensure consistency
POLICY_TYPES_ORDER: list[str] = ['ordinary life', 'industrial life', 'credit life', 'group life']
POLICY_COLORS: list[str] = ['lightgreen', 'mediumpurple', 'lightskyblue', 'peachpuff']

# --- Helper Functions for Data Loading and Cleaning ---

def load_and_prep_sheet(filepath: Path, sheet_name: str, rows_to_keep: list[int], type_label: str) -> pd.DataFrame:
    """
    Reads a specific sheet from an Excel file, selects given rows, and adds a type label.
    """
    df = pd.read_excel(filepath, sheet_name=sheet_name, skiprows=8).iloc[rows_to_keep]
    df.rename(columns={df.columns[0]: "Status"}, inplace=True)
    
    df["Status"] = (
        df["Status"]
        .str.replace(" in ", ": In ", regex=False)
        .str.split(": ", n=1, expand=True)[1]
    )
    
    df.loc['total']=df[df["Status"].str.contains("Lapsed|Surrendered", na=False, regex=True)].sum()
    df["Status"] = df["Status"].str.replace("SurrenderedLapsed", "Terminated") 


    # Remove " Y" suffix from year columns
    df.columns = df.columns.str.replace(" Y", "", regex=False)
    df["Type"] = type_label
    return df

def prepare_plot_data(df: pd.DataFrame, metric_name: str, status: str) -> pd.DataFrame:
    """
    Filters for 'In Force' status, melts the DataFrame from wide to long format,
    and pre-calculates total values and percentages for plotting.
    """
    id_cols = ["Type", "Status"]
    year_cols = [col for col in df.columns if col not in id_cols]

    # Filter for 'In Force' status and reshape
    df_long = df[df["Status"] == status].melt(
        id_vars=["Type"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value",
    )
    
    # Convert year to numeric for sorting and calculations
    df_long["Year"] = pd.to_numeric(df_long["Year"])
    df_long["Metric"] = metric_name

    # --- Pre-calculation for plotting ---
    # Calculate the total value for each year (sum of all policy types)
    total_per_year = df_long.groupby("Year")["Value"].transform("sum")
    
    # Calculate the percentage of each type relative to the yearly total
    df_long["Percentage"] = (df_long["Value"] / total_per_year) * 100
    
    return df_long

# --- Plotting Function ---

def plot_stacked_bars(
    axis: Axes,
    data: pd.DataFrame,
    years: np.ndarray,
    x_coords: np.ndarray,
    offset: float,
    bar_label: str,
    scale: float,
    width: float = 0.35,
) -> None:
    """
    Draws a single stacked bar on a given axis and adds percentage labels
    for the 'ordinary life' category.
    """
    bottom = np.zeros(len(years))
    
    for i, p_type in enumerate(POLICY_TYPES_ORDER):
        # Filter for the specific policy type and align with years
        type_data = data[data["Type"] == p_type].set_index("Year").reindex(years).fillna(0)
   
      
        values = type_data["Value"] / scale

        axis.bar(
            x_coords + offset,
            values,
            width,
            label=p_type,
            bottom=bottom,
            color=POLICY_COLORS[i],
            alpha=0.8,
        )
        
        # --- Add Percentage Label for 'ordinary life' ---
        if p_type == 'ordinary life':
            percentages = type_data["Percentage"]
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

                axis.text(
                    x=x_coords[idx] + offset,
                    y=bottom[idx] + values.iloc[idx], # Position at the top of the segment
                    s=round(values.iloc[idx]),
                    ha='center',
                    va='top', # Align bottom of text with the y-coordinate
                    fontsize=9,
                )
        
                # add text for total value at the top of each bar
        # print(values.values)
        bottom += values.values

    for x, y in zip(x_coords, bottom):

        axis.text(
                        x=x + offset,
                        y=y, # Position at the top of the segment
                        s=round(y),
                        ha='center',
                        va='bottom', # Align bottom of text with the y-coordinate
                        fontsize=10,
                        fontweight='bold',
                    )
    
    # Format the axis
    axis.set_ylabel(bar_label, weight='bold', fontsize=12)


# --- Main Logic ---

num_policies = pd.concat([
    load_and_prep_sheet(EXCEL_PATH, f"{base} - Number of Policies", num_rows, label)
    for base, label, num_rows, _ in POLICY_CONFIGS
], ignore_index=True)
amount_insurance = pd.concat([
    load_and_prep_sheet(EXCEL_PATH, f"{base} - Amount of Insurance", amount_rows, label)
    for base, label, _, amount_rows in POLICY_CONFIGS
], ignore_index=True)

for stts in ["In Force", "Terminated"]:
    num_plot_data = prepare_plot_data(num_policies, "Number of Policies", status=stts)
    amount_plot_data = prepare_plot_data(amount_insurance, "Face Value of Insurance", status=stts)

    # 4. Setup Plotting Environment
    YEARS = sorted(num_plot_data["Year"].unique())
    x = np.arange(len(YEARS))  # the label locations
    bar_width = 0.35  # the width of each bar group

    fig, ax1 = plt.subplots(figsize=(18, 10))
    ax2 = ax1.twinx()  # Create a second y-axis sharing the x-axis

    # 5. Plot the Data
    # Plot 'Number of Policies' on the primary axis (ax1)
    plot_stacked_bars(
        axis=ax1,
        data=num_plot_data,
        years=YEARS,
        x_coords=x,
        offset=-bar_width / 1.7,
        bar_label="Number of Policies (in millions)",
        scale=1e6, # Values are in single units, scale to millions
        width=bar_width
    )

    # Plot 'Amount of Insurance' on the secondary axis (ax2)
    # Note: Excel values are already in thousands, so 1e9 makes it trillions
    plot_stacked_bars(
        axis=ax2,
        data=amount_plot_data,
        years=YEARS,
        x_coords=x,
        offset=bar_width / 1.7,
        bar_label="Amount of Insurance (in $ trillions)",
        scale=1e9, # Values are in thousands, scale to trillions (1,000 * 1e9 = 1e12)
        width=bar_width
    )

    # # --- Final Chart Formatting ---
    # ax1.set_xlabel("Year", weight='bold', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(YEARS)
    # ax1.tick_params(axis='x', labelsize=12)
    # ax1.tick_params(axis='y', labelsize=12)
    # ax2.tick_params(axis='y', labelsize=12)

    # Create a single, shared legend
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

    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    fig.tight_layout(rect=[0, 0, 1, 0.95]) # Adjust layout to make room for title and legend
    plt.show()