"""
Plot value lost waterfall
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER
from scripts.plot_moneyleft import (
    money_left_15_T,
    mortality_experience,
    sample_representativeness,
)


EEV = "Excess_Policy_PV_VBT01_lapseTrue_mort1_coihike_0"

fees = {
    "life_settlement": {
        "broker_fee": 0.08,
        "management_fee": 0.015,
        "performance_fee": 0.1,
    },
}

for key, value in fees.items():
    BROKER_FEE = value["broker_fee"]
    MANAGEMENT_FEE = value["management_fee"]
    PERFORMANCE_FEE = value["performance_fee"]
    PROVIDER_FEE = 0.005


    mortality_experience = pd.read_excel(DATA_FOLDER / f"mortality_experience_{key}.xlsx")

    broker_fee = (
        sum(
            mortality_experience["broker_fee_rate"]
            * mortality_experience["Amount Exposed"]
        )
        * sample_representativeness
    )

    provider_fee = (
        sum(
            mortality_experience["provider_fee_rate"]
            * mortality_experience["Amount Exposed"]
        )
        * sample_representativeness
    )

    management_fee = (
        sum(
            mortality_experience["management_fee_rate"]
            * mortality_experience["Amount Exposed"]
        )
        * sample_representativeness
    )

    performance_fee = (
        sum(
            mortality_experience["performance_fee_rate"]
            * mortality_experience["Amount Exposed"]
        )
        * sample_representativeness
    )

    policyholder_lump_sum = sum(mortality_experience["policyholder_lump_sum"]*mortality_experience["Amount Exposed"])*sample_representativeness

    SCALE = 1e9  # <--- Factored out order of magnitude

    # 1. Define Labels and Raw Values
    y_labels = [
        "Life insurance value\nto policyholders",
        "Policyholder lump sum",
        "Broker fee",
        "Value at settlement",
        "Provider fee",
        "Management fee",
        "Performance fee",
        "Investor profit",
    ]

    # Use 0 for "Total" rows (Value at settlement, Investor profit)
    # Use negative numbers for subtractions
    raw_values = [
        money_left_15_T,
        -policyholder_lump_sum,
        -broker_fee,
        0,
        -provider_fee,  # Intermediate total
        -management_fee,
        -performance_fee,
        0,  # Final total
    ]

    # Define which rows are "Totals" (resets base to 0) vs "Relative" (adjusts previous base)
    # True = Total/Absolute, False = Relative/Subtraction
    is_total = [True, False, False, True, False, False, False, True]

    # 2. Calculate Plotting Coordinates
    scaled_values = [x / SCALE for x in raw_values]
    
    # Lists to hold bar parameters
    lefts = []
    widths = []
    colors = []
    text_labels = []
    
    current_sum = 0.0
    
    # Using standard Matplotlib colors here:
    C_TOTAL = 'green'  # Blue
    C_NEG = 'red'    # Red
    
    for val, total_flag in zip(scaled_values, is_total):
        if total_flag:
            # Calculate the implied value for the Total bars
            if val == 0: 
                val = current_sum
            
            lefts.append(0)
            widths.append(val)
            colors.append(C_TOTAL)
            current_sum = val # Reset current sum reference to this total
        else:
            # For relative bars (subtractions in this context)
            # Since val is negative, we add it to current_sum to find the new floor
            # The bar starts at the new floor and goes up by abs(val)
            lefts.append(current_sum + val) 
            widths.append(abs(val))
            colors.append(C_NEG)
            current_sum += val
        
        text_labels.append(f"{val if total_flag else abs(val):.2f}")

    # 3. Create Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Indices for bars (reversed logic not strictly needed if we invert axis later, 
    # but 0-index usually at bottom in MPL)
    y_pos = np.arange(len(y_labels))

    bars = ax.barh(y_pos, widths, left=lefts, color=colors, height=0.6, edgecolor='black', alpha=0.8)

    # 4. Add Connectors and Text
    for i in range(len(y_labels)):
        # Add Text Value
        # Position text slightly right of the bar
        val_x = lefts[i] + widths[i] + (1500 * 0.01) # small offset
        ax.text(val_x, i, text_labels[i], va='center', fontweight='bold')

        # Add Connector Lines (between this bar and the next)
        if i < len(y_labels) - 1:
            # Determining the "step" edge. 
            # If current is Total, step is at width.
            # If current is Relative (subtraction), step is at left edge (the new lower value).
            if is_total[i]:
                step_x = widths[i]
            else:
                step_x = lefts[i]
            
            # Draw vertical line to the next bar
            ax.plot([step_x, step_x], [i, i + 1], color='grey', linestyle='--', linewidth=1)

    # 5. Formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    ax.invert_yaxis() # Put the first entry at the top

    ax.set_xlabel("billion USD")
    # ax.set_title("With {} fee scheme".format(key))
    
    # Mimic the layout_xaxis_range=[-100, 1500]
    # Scaled by 1e9 already, so just use raw numbers
    ax.set_xlim(0, 1500) 

    # Remove top/right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    
    plt.show() # Optional: Uncomment to view interactively
    
    # Save figure
    fig.savefig(FIGURE_FOLDER / "waterfall.pdf")
    plt.close(fig) # Close to free memory