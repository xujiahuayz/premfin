import brewer2mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from premiumFinance.constants import FIGURE_FOLDER
from premiumFinance.fetchdata import get_market_size
from scripts.sample_represent import mortality_experience, sample_representativeness


def get_money_left(
    current_vbt: str = "VBT15",
    lapse_assumption: bool = True,
    current_mort: float = 1,
    premium_hike: float = 0,
) -> float:
    """
    get money left value in different scenarios
    """
    return (
        sum(
            w
            for w in mortality_experience[
                f"Excess_Policy_PV_{current_vbt}_lapse{lapse_assumption}_mort{current_mort}_coihike_{premium_hike}"
            ]
            * mortality_experience["Amount Exposed"]
        )
        * sample_representativeness
    )


money_left_15_T = get_money_left(current_vbt="VBT15", lapse_assumption=True)

if __name__ == "__main__":
    # money_left_01_T = get_money_left(current_vbt="VBT01", lapse_assumption=True)
    # money_left_15_F = get_money_left(current_vbt="VBT15", lapse_assumption=False)

    # https://www.federalreserve.gov/releases/z1/20120607/z1.pdf page 113
    real_estate_nominal = 23523.6 / 1e3

    # change from 2007-2009
    real_estate_change = (23523.6 - 18874.5) / 1e3

    WIDTH = 1
    # %%
    bmap_5 = brewer2mpl.get_map("greens", "sequential", 5)
    bmap_3 = brewer2mpl.get_map("dark2", "qualitative", 3)
    colors = bmap_3.mpl_colors
    colors_5 = bmap_5.mpl_colors
    colors.extend(colors_5[::-1])
    # %%

    # %% latest plot
    heights = [
        real_estate_nominal,
        get_market_size(year=2024) / 1e12,
        real_estate_change,
        # money_left_01_T / 1e12,
        money_left_15_T / 1e12,
        # money_left_15_F / 1e12,
    ]

    x_pos = [0, WIDTH, 3 * WIDTH, 4 * WIDTH]

    plt.bar(
        x=x_pos,
        height=heights,
        width=WIDTH,
        color=['blue','green','blue','green'],
        edgecolor="k",
    )


    for i, h in enumerate(heights):
        plt.text(
            x=x_pos[i],
            y=1.02 * heights[i],
            s="{:.2f}".format(heights[i]),
            ha="center",
            va="bottom",
            rotation=0,
        )

    plt.xticks(
        x_pos,
        [
            "Real estate market size",
            "Life insurance face amount",
            "Real estate value lost",
            "Life insurance value to policyholders",
        ],
        rotation=45,
    )

    plt.ylabel("trillion USD")
    # ylim
    plt.ylim(0, 42)

    plt.tight_layout()
    plt.savefig(FIGURE_FOLDER / "moneyleft.pdf")
    plt.show()
