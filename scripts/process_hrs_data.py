import pandas as pd
from premiumFinance.constants import DATA_FOLDER

# Path to the .sas7bdat file
file_path = DATA_FOLDER / "HRS/h20core/h20sta/H20T_R.dta"

data = pd.read_stata(file_path)

# count of different values in a column "RT040"
# https://hrs.isr.umich.edu/sites/default/files/meta/2020/core/codebook/h20t_ri.htm
data["RT040"].value_counts()
