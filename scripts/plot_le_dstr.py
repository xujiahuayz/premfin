import pandas as pd
from matplotlib import pyplot as plt

from premiumFinance.constants import FIGURE_FOLDER, DOLLAR_MAGNITUDES
from scripts.process_mortality_table import mortality_experience


def le_distr(
    col_name: str,
    scale_down: int,
    y_label: str,
    df: pd.DataFrame = mortality_experience,
):
    # create a column of life_expectancy bin
    df["le_bin"] = pd.cut(df["life_expectancy"], bins=range(0, 90, 10))
    df[col_name] = df[col_name] / 10**scale_down

    money_left_by_le = df.groupby("le_bin")[col_name].sum().reset_index()

    # plot the distribution of money left by life expectancy
    fig, ax = plt.subplots()
    ax.bar(
        x=money_left_by_le["le_bin"].astype(str),
        height=money_left_by_le[col_name],
    )
    # add value labels
    for i, v in enumerate(money_left_by_le[col_name]):
        ax.text(
            i,
            v,
            round(v, 2),
            ha="center",
            verticalalignment="bottom",
        )

    ax.set_xlabel("Life expectancy")
    ax.set_ylabel(f"{y_label} ({DOLLAR_MAGNITUDES[scale_down]} USD)")

    # save figure pdf
    fig.savefig(str(FIGURE_FOLDER / f"le_dstr_{col_name}.pdf"), bbox_inches="tight")
    plt.show()


le_distr("money_left", 12, y_label="Life insurance value to policyholders")
le_distr("lapsed_economic_value", 9, y_label="Lapsed economic value")
