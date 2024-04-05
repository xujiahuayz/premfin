from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from premiumFinance.constants import DATA_FOLDER, MORTALITY_TABLE_CLEANED_PATH
from scripts.process_mortality_table import mortality_experience
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.families.links import Logit


AAPARTNERS_PATH = DATA_FOLDER / "2016 Medical Underwriting final.xlsx"
AAPARTNERS_SHEET = "Full Sample"

# get dataframe from MORALITY_TABLE_CLEANED_PATH

mortality_experience = pd.read_excel(
    MORTALITY_TABLE_CLEANED_PATH,
    engine="openpyxl",
)

# get the start of issue_age_group by getting 2 digits from the start of the string
mortality_experience["issue_age_group_start"] = (
    mortality_experience["Issue Age Group"].str.extract(r"(\d{2})").astype(int)
)
issue_age_group_start = mortality_experience["issue_age_group_start"].unique()

mortality_experience["attained_age_group_start"] = (
    mortality_experience["Attained Age Group"].str.extract(r"(\d{2})").astype(int)
)
attained_age_group_start = mortality_experience["attained_age_group_start"].unique()

# read "Full Sample" tab from "2016 Medical Underwriting final.xlsx" from DATA_FOLDER, A:S
aapartners = pd.read_excel(
    AAPARTNERS_PATH,
    sheet_name=AAPARTNERS_SHEET,
    engine="openpyxl",
    usecols="A:S,AA",
)


# # get issueage from IssDate and Birthday, get exact number of days from IssDate and Birthday

aapartners["issueage"] = (
    aapartners["IssDate"] - aapartners["Birthday"]
).dt.days / 365.2425


aapartners["isSmoker"] = aapartners["Smoker"].map(lambda x: {"NS": False, "S": True}[x])
# # get isMale, {"M": True, "F": False}, use None for all other values
aapartners["isMale"] = aapartners["Gender"].map(
    lambda x: {"M": True, "F": False}.get(x, None)
)


aapartners = aapartners.dropna(subset=["TP", "FA", "isMale", "Blended"])
# make TP/FA between 0 and 1, max(min(1, aapartners["TP/FA"]), 0)
aapartners["TPR"] = aapartners["TP/FA"].clip(0, 1)


# run beta-regression  "TP/FA" ~ ln(Blended), where TP/FA is valued between 0 and 1
# Compute the natural logarithm of 'Blended'
aapartners["le"] = aapartners["Blended"] / 12
aapartners["ln_le"] = np.log(aapartners["le"])

# Fit the beta regression model
model_formula = "TPR ~ ln_le"
tpr_model = smf.glm(
    formula=model_formula, data=aapartners, family=sm.families.Binomial(link=Logit())
).fit()


if __name__ == "__main__":

    # scatter plot TP/FA and Blended, isMale True blue, isMale False red, isSmoker True marker "x", isSmoker False marker "o"
    for isMale, marker in zip([True, False], [".", "x"]):  # Define marker styles
        for isSmoker, color in zip([True, False], ["red", "blue"]):  # Define colors
            # Filter the DataFrame for each subgroup
            subgroup = aapartners[
                (aapartners["isMale"] == isMale) & (aapartners["isSmoker"] == isSmoker)
            ]
            plt.scatter(
                subgroup["le"],
                subgroup["TPR"],
                c=color,  # Color based on 'isMale'
                marker=marker,  # Marker based on 'isSmoker'
                alpha=0.2,
                label=f'{"Male" if isMale else "Female"}, {"Smoker" if isSmoker else "Non-Smoker"}',
            )

    plt.xlabel("LE")
    plt.ylabel("TPR")

    plt.legend(ncol=2)

    # Plot the regression line
    # Generate x values in the original 'Blended' scale
    x = np.linspace(aapartners["le"].min(), aapartners["le"].max(), 100)

    # Use the model to predict on the transformed scale of 'Blended'
    y_pred = tpr_model.predict(pd.DataFrame({"ln_le": np.log(x)}))

    # Plot the regression line
    plt.plot(x, y_pred, color="black", linestyle="--", label="Regression Line")

    # log x-axis
    plt.xscale("log")

    plt.show()
