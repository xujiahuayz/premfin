from typing import Iterable

from matplotlib import pyplot as plt
import numpy as np
from scipy import optimize

from premiumFinance.constants import FIGURE_FOLDER, DATA_FOLDER
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured
from premiumFinance.treasury_yield import yield_curve
from premiumFinance.util import cash_flow_pv
from scripts.process_aapartners import tpr_model
from scripts.process_mortality_table import (
    mortality_experience,
    # sample_representativeness,
)
import pickle

colors = {(0, 100): "blue", (0, 30): "green", (50, 100): "red"}
# based on logged mortality_experience['life_expectancy'] get tpr

mortality_experience["ln_le"] = np.log(mortality_experience["life_expectancy"])
mortality_experience["tpr"] = tpr_model.predict(mortality_experience)


def condiscounted_cash_flow(
    row,
    currentVBT: str = "VBT15",
    currentmort: float = 1.0,
    is_level_premium: bool = True,
    lapse_assumption: bool | float = True,
    policyholder_rate: float | Iterable[float] = yield_curve,
    statutory_interest=0.035,
    premium_markup=0.0,
    cash_interest=0.03,
    lender_coc=0.01,
) -> list[float]:
    this_insured = Insured(
        issue_age=row["issueage"],  # type: ignore
        is_male=row["isMale"],  # type: ignore
        is_smoker=row["isSmoker"],  # type: ignore
        current_age=row["currentage"],  # type: ignore
        issue_vbt="VBT01",
        current_vbt=currentVBT,
        current_mortality_factor=currentmort,
    )
    this_policy = InsurancePolicy(
        insured=this_insured,
        is_level_premium=is_level_premium,
        lapse_assumption=lapse_assumption,
        statutory_interest=statutory_interest,
        premium_markup=premium_markup,
        policyholder_rate=policyholder_rate,
        cash_interest=cash_interest,
    )
    this_financing = PolicyFinancingScheme(this_policy, lender_coc=lender_coc)
    return this_financing.policy.policy_value_list(
        issuer_perspective=False,
        at_issue=False,
        discount_rate=0,
    )


if __name__ == "__main__":

    results = []
    for lapse_multiplier in [0, 0.5, 1]:
        for mort_mult in [1, 3]:
            probablistic_cash_flows_rate_df = mortality_experience.apply(
                lambda row: [
                    -w
                    for w in condiscounted_cash_flow(
                        row=row,
                        currentmort=mort_mult,
                        lapse_assumption=lapse_multiplier,
                    )
                ],
                axis=1,
                result_type="expand",
            )

            for tp_factor in [0, 0.1, 0.3, 0.5, 0.8, 1, 1.2, 1.5]:
                # make a copy for probablistic_cash_flows_rate
                probablistic_cash_flows_rate = probablistic_cash_flows_rate_df.copy()

                mortality_experience["tp_rate"] = (
                    mortality_experience["tpr"] * tp_factor
                    + mortality_experience["surrender_left"]
                ).clip(
                    0, 1
                )  # make sure tp_rate is between 0 and 90%

                ## deduct transaction cost times tp_factor for column 0
                probablistic_cash_flows_rate[0] -= mortality_experience["tp_rate"]

                # for each row, multiply rate by amount exposed, lapse_rate and sample_representativeness
                probablistic_cash_flows = probablistic_cash_flows_rate.mul(
                    mortality_experience["Amount Exposed"]
                    * mortality_experience["lapse_rate"]
                    # * sample_representativeness
                    ,
                    axis=0,
                )

                # # # deduct transaction cost times tp_factor for column 0
                # probablistic_cash_flows[0] -= (
                #     mortality_experience["Amount Exposed"]
                #     * mortality_experience["tp_rate"]
                #     # * 0.01
                # )
                for ranges, color in colors.items():

                    aggregated_cash_flow = probablistic_cash_flows[
                        mortality_experience["life_expectancy"].between(*ranges)
                    ].sum(axis=0)

                    # calculate Macaulay Duration using the aggregated cash flow and yield curve
                    pv_cash_flow = cash_flow_pv(
                        cashflow=aggregated_cash_flow,
                        probabilities=1,
                        discounters=yield_curve,
                    )
                    time_weighted_cash_flow = [
                        t * c for t, c in enumerate(pv_cash_flow, start=0)
                    ]
                    macaulay_duration = sum(time_weighted_cash_flow) / sum(pv_cash_flow)

                    sol = optimize.root_scalar(
                        lambda r: sum(
                            cash_flow_pv(
                                cashflow=aggregated_cash_flow,
                                probabilities=1,
                                discounters=r,
                            )
                        ),
                        x0=0.1,
                        bracket=[-0.6, 2],
                        method="brentq",
                    )

                    # save result to dict
                    results.append(
                        {
                            "tp_factor": tp_factor,
                            "mort_mult": mort_mult,
                            "lapse_multiplier": lapse_multiplier,
                            "ranges": ranges,
                            "irr": sol.root,
                            "macaulay": macaulay_duration,
                            "aggregated_cash_flow": aggregated_cash_flow,
                        }
                    )

                    # normalize aggregated_cash_flow such that initial cash flow is -1
                    aggregated_cash_flow /= -aggregated_cash_flow[0]

                    plt.bar(
                        x=range(len(aggregated_cash_flow)),
                        height=aggregated_cash_flow,
                        alpha=0.3,
                        # contour with solid line
                        edgecolor="black",
                        label=f"LE range: {ranges} \nIRR: {sol.root*100:.2f}%",
                        # + f" \n Macaulay Duration: {macaulay_duration:.2f}",
                    )

                    plt.xlabel("Year since portfolio establishment")
                    plt.ylabel("Normalized cash flow")
                    plt.xlim(-2, 107)

                plt.legend()

                plt.title(
                    f"price multiplier: {tp_factor}, mortality multiplier: {mort_mult}"
                )

                # save to pdf
                plt.savefig(
                    FIGURE_FOLDER
                    / f"tp_factor_{tp_factor}_mort_mult_{mort_mult}_lapse_{lapse_multiplier}.pdf",
                    bbox_inches="tight",
                )

                plt.show()

    # save results to pickle

    with open(DATA_FOLDER / "irr_results_lapse.pickle", "wb") as f:
        pickle.dump(results, f)
