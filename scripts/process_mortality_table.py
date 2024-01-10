from premiumFinance.util import lapse_rate
from scripts.sample_represent import mortality_experience, sample_representativeness

current_vbt: str = "VBT15"
lapse_assumption: bool = True
current_mort: float = 1
premium_hike: float = 0

mortality_experience["money_left"] = (
    mortality_experience[
        f"Excess_Policy_PV_{current_vbt}_lapse{lapse_assumption}_mort{current_mort}_coihike_{premium_hike}"
    ]
    * mortality_experience["Amount Exposed"]
    * sample_representativeness
)


mortality_experience["lapse_rate"] = mortality_experience.apply(
    lambda row: lapse_rate(isMale=row["isMale"])[row["currentage"] - row["issueage"]],
    axis=1,
)

mortality_experience["number_lapsed_policies"] = (
    mortality_experience["lapse_rate"] * mortality_experience["Policies Exposed"]
)

mortality_experience["average_lapsed_amount"] = (
    mortality_experience[
        f"Excess_Policy_PV_{current_vbt}_lapse{lapse_assumption}_mort{current_mort}_coihike_{premium_hike}"
    ]
    * mortality_experience["Amount Exposed"]
    / mortality_experience["Policies Exposed"]
)

mortality_experience["lapsed_economic_value"] = (
    mortality_experience["lapse_rate"]
    * mortality_experience[
        f"Excess_Policy_PV_{current_vbt}_lapse{lapse_assumption}_mort{current_mort}_coihike_{premium_hike}"
    ]
    * mortality_experience["Amount Exposed"]
    * sample_representativeness
)
