from premiumFinance.constants import DATA_FOLDER
from premiumFinance.util import lapse_rate

import pandas as pd
from os import path



untapped_profit_path = path.join(DATA_FOLDER, "untappedprofit_cnt.xlsx")
mortality_experience = pd.read_excel(untapped_profit_path)

mortality_experience["lapse_rate"] = mortality_experience.apply(
    lambda row: lapse_rate(isMale=row["isMale"])[row["currentage"] - row["issueage"]],
    axis=1,
)


mortality_experience["number_lapsed_policies"] = (
    mortality_experience["lapse_rate"] * mortality_experience["Policies Exposed"]
)

mortality_experience["average_lapsed_amount"] = (
    mortality_experience["Excess_Policy_PV_yield_curve"]
    * mortality_experience["Amount Exposed"]
    / mortality_experience["Policies Exposed"]
)