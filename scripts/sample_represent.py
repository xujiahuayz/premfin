import pandas as pd

from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH
from premiumFinance.fetchdata import get_market_size

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)
sample_representativeness = (
    get_market_size(year=2024) / mortality_experience["Amount Exposed"].sum()
)
