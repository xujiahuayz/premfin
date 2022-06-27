#%%
import pandas as pd
import numpy as np

# %%
data_reader = pd.read_stata(
    "/Users/tammy/Java_Help/testVS/premfin/data/pu2020.dta",
    chunksize=1000,
    columns=["TNETWORTH", "WPFINWGT", "TLIFE_FVAL"],
)

# %%
frame_1 = pd.DataFrame()
for i in range(10):
    chunk_1 = data_reader.get_chunk(1000)
    chunk_1_filtered = chunk_1.dropna()
    frame_1 = frame_1.append(chunk_1_filtered)

#%%
omd = pd.read_excel(
    "/Users/tammy/Java_Help/testVS/premfin/data/OrganizedMortalityDistribution.xlsx",
    header=None,
)

omd = omd.drop(omd.index[0])  # delete blank row.
new_header = omd.iloc[0]  # replace header with first row.
omd = omd[1:]
omd.columns = new_header

omd = omd.drop(
    columns=[
        "Amount Exposed ",
        "Policies Exposed ",
        "Death Claim Amount ",
        "Sum of Number of Deaths",
        "Count of Face Amount Band",
    ]
)

#%%
utp = pd.read_excel("/Users/tammy/Java_Help/testVS/premfin/data/untappedprofit.xlsx")

utp = utp.drop(
    columns=[
        "Amount Exposed",
        "Policies Exposed",
        "Excess_Policy_PV_0",
        "Excess_Policy_PV_0.01",
        "Excess_Policy_PV_0.02",
        "Excess_Policy_PV_0.05",
        "Excess_Policy_PV_0.1",
        "Excess_Policy_PV_0.2",
        "Excess_Policy_PV_0.5",
        "Surrender value",
        "Max Loan rate",
        "Lender profit",
        "Dollar profit",
    ]
)

# change column names to match.
utp = utp.rename(
    columns={
        "isMale": "Gender",
        "isSmoker": "Smoker Status",
        "issueage": "Issue Age Group",
        "currentage": "Attained Age Group",
    }
)
