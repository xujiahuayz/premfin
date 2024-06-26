from matplotlib import pyplot as plt
from scripts.process_mortality_table import mortality_experience


df = mortality_experience[
    mortality_experience["isMale"] & (mortality_experience["isSmoker"] == 1)
]

fig, ax = plt.subplots()
# one line for issue age
colors = ["r", "g", "b", "y"]
for i, issueage in enumerate(df["issueage"].unique()[[1, 5, 9, 13]]):
    df_plot = df[df["issueage"] == issueage]

    ax.plot(
        df_plot["policy_age"],
        df_plot["surrender_value"],
        label=f"issue age {issueage}",
        color=colors[i],
    )

    ax.plot(
        df_plot["policy_age"],
        df_plot["surrender_left"],
        linestyle="--",
        color=colors[i],
    )
ax.set_xlabel("Policy Age")
ax.set_ylabel("Fraction of Face Value")
plt.legend()
