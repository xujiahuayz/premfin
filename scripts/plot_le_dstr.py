import pandas as pd
from scripts.sample_represent import mortality_experience, sample_representativeness
from matplotlib import pyplot as plt

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
    / 1e12
)

# create a column of life_expectancy bin
mortality_experience["le_bin"] = pd.cut(
    mortality_experience["life_expectancy"], bins=range(0, 90, 10)
)

money_left_by_le = (
    mortality_experience.groupby("le_bin")["money_left"].sum().reset_index()
)

# plot the distribution of money left by life expectancy
fig, ax = plt.subplots()
ax.bar(
    x=money_left_by_le["le_bin"].astype(str),
    height=money_left_by_le["money_left"],
)
# add value labels
for i, v in enumerate(money_left_by_le["money_left"]):
    ax.text(
        i,
        v,
        round(v, 2),
        ha="center",
        verticalalignment="bottom",
    )


ax.set_xlabel("Life expectancy")
ax.set_ylabel("Life insurance value to policyholders (trillion USD)")
