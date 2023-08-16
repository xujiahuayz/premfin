import pandas as pd
from premiumFinance.constants import DATA_FOLDER

# Path to the .sas7bdat file
file_path = DATA_FOLDER / "HRS/h20core/h20sta/H20T_R.dta"

data = pd.read_stata(file_path)
