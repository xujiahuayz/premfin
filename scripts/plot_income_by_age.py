import pandas as pd
from os import path
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np


from premiumFinance.constants import (
    PROJECT_ROOT,
    DATA_FOLDER,
    FIGURE_FOLDER,
    DATE_ID,
    AGE_BIN,
    AGE_BREAKPOINTS,
)
from premiumFinance.util import median_
from process_mortality_table import mortality_experience


mortality_experience["age_bin"] = mortality_experience.apply(
    lambda row: AGE_BIN[np.min(np.where(row["currentage"] < AGE_BREAKPOINTS))], axis=1
)

median_value_loss_by_age = [
    median_(
        list(
            mortality_experience.loc[mortality_experience["age_bin"] == w][
                ["average_lapsed_amount", "Policies Exposed"]
            ].itertuples(index=False, name=None)
        )
    )
    for w in AGE_BIN
]


if __name__ == "__main__":
    INDEX_NAME = "year"
    health_income_demography = {}
    for account in DATE_ID:
        health_income_demography[account] = pd.DataFrame(columns=[INDEX_NAME])
        for age, w in DATE_ID[account].items():
            new_pd = pd.read_csv(
                path.join(PROJECT_ROOT, DATA_FOLDER, w + ".csv"),
                names=[INDEX_NAME, age],
                header=1,
            )
            health_income_demography[account] = health_income_demography[account].merge(
                new_pd, how="outer", on=INDEX_NAME
            )
            health_income_demography[account].set_index(INDEX_NAME, inplace=True)

    health_income_ratio = health_income_demography["Expenditures_Healthcare"].div(
        health_income_demography["Income_After_Taxes"]
    )

    data_to_plot = health_income_ratio.loc["2020-01-01"]

    plt.subplots()

    ax0 = pd.Series(median_value_loss_by_age).plot(kind="bar", color="y")
    ax0.set_ylabel("median loss due to life policy lapse")
    ax0.set_xlabel("age")

    ax = data_to_plot.plot(marker=".", secondary_y=True)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=0))

    ax.set_ylabel("annual health expenditure / income")

    for i, x in enumerate(data_to_plot):
        ax.annotate("{:.1%}".format(x), (i, x), ha="center")

    plt.savefig(path.join(FIGURE_FOLDER, "health_income_ratio.pdf"))
