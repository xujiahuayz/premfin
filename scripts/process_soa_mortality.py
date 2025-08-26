# process a large dataset from DATA_FOLDER/SOA/ILEC_2012_19 - 20240429.txt with over 50 million rows

from matplotlib.axes import Axes
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from premiumFinance.constants import DATA_FOLDER


# read ILEC 2012_19 - Data Dictionary.xlsx the first tab "Data Dictionary" to understand the column type

data_dictionary = pd.read_excel(DATA_FOLDER / "SOA" / "ILEC 2012_19 - Data Dictionary.xlsx", sheet_name="Data Dictionary")
# convert "Field" and "Type" columns to a dictionary
# change Numeric, String, and Decimal to int, str, and float respectively in data_types
data_types = {
    key: (
        int if value == "Numeric" else
        str if value == "String" else
        float if value == "Decimal" else
        value  # Keep other types as is
    )
    for key, value in zip(data_dictionary["Field"], data_dictionary["Type"])
}

# the first row is the header, and the file is tab-separated
chunk_size = 10**6  # Adjust chunk size as needed
mortality_data_chunks = pd.read_csv(
    DATA_FOLDER / "SOA" / "ILEC_2012_19 - 20240429.txt",
    sep="\t",
    header=0,
    chunksize=chunk_size,
    dtype=data_types
)
# Concatenate all chunks into a single DataFrame
mortality_data = pd.concat(mortality_data_chunks, ignore_index=True)

# quick check of duration calculation
duration_check = mortality_data['Attained_Age'] - mortality_data['Issue_Age'] + 1 - mortality_data['Duration']
(duration_check == 0).all()

# quick check of Face_Amount_Band
mortality_data['Average_Face_Amount'] = mortality_data['Amount_Exposed'] / mortality_data['Policies_Exposed']
# parse the Face_Amount_Band 05: 100,000 - 249,999 to get the lower and upper bounds
mortality_data[['Face_Amount_ID', 'Face_Amount_Lower', 'Face_amount_Upper']] = mortality_data['Face_Amount_Band'].str.replace(',', '').str.extract(
    r'(\d+):\s*([\d,]+)(?:\s*-\s*([\d,]+)|\+)'
    ).astype(float)

# take the lower band if missing value for Average_Face_Amount
mortality_data['Average_Face_Amount'] = mortality_data['Average_Face_Amount'].fillna(mortality_data['Face_Amount_Lower'])
# check if average face amount is within the bounds
(mortality_data['Average_Face_Amount'] >= (mortality_data['Face_Amount_Lower'] - 5)).all()


mortality_data.to_pickle(DATA_FOLDER / "SOA" / "mortality_data.pkl")



# save to a zipped pickle file
# 