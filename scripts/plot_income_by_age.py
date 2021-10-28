from numpy import right_shift
import pandas as pd
from os import path
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


from fetch_fred import DATE_ID
from premiumFinance.constants import PROJECT_ROOT, DATA_FOLDER, FIGURE_FOLDER


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
    ax = data_to_plot.plot(marker=".")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=2))
    ax.set_xlabel("age")
    ax.set_ylabel("annual health expenditure / income")

    for i, x in enumerate(data_to_plot):
        ax.annotate("{:.1%}".format(x), (i, x), ha="center")

    plt.savefig(path.join(FIGURE_FOLDER, "health_income_ratio.pdf"))
