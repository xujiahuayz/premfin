from typing import Iterable

import numpy as np
from scipy import optimize

from premiumFinance.constants import DATA_FOLDER
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured
from premiumFinance.treasury_yield import yield_curve
from premiumFinance.util import cash_flow_pv
from scripts.process_aapartners import tpr_model
from scripts.process_mortality_table import (
    mortality_experience,
    sample_representativeness,
)
import pickle


# based on logged mortality_experience['life_expectancy'] get tpr

mortality_experience["ln_le"] = np.log(mortality_experience["life_expectancy"])
mortality_experience["tpr"] = tpr_model.predict(mortality_experience)


def condiscounted_cash_flow(
    row,
    currentVBT: str = "VBT15",
    currentmort: float = 1.0,
    is_level_premium: bool = True,
    lapse_assumption: bool = True,
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
    for premium_markup in [0, 0.1, 0.2]:
        for mort_mult in [1]:
            probablistic_cash_flows_df = mortality_experience.apply(
                lambda row: [
                    -w
                    for w in condiscounted_cash_flow(
                        row=row, currentmort=mort_mult, premium_markup=premium_markup
                    )
                ],
                axis=1,
                result_type="expand",
            )

            for tp_factor in [0, 0.5, 1, 1.5]:
                # make a copy for probablistic_cash_flows_rate
                probablistic_cash_flows_rate = probablistic_cash_flows_df.copy()

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

                for maxle in [
                    # 1,
                    5,
                    10,
                    15,
                    20,
                    25,
                    30,
                    40,
                    50,
                    60,
                    70,
                    80,
                    90,
                    100,
                ]:
                    row_range = mortality_experience["life_expectancy"].between(
                        *(0, maxle)
                    )
                    aggregated_cash_flow = probablistic_cash_flows[row_range].sum(
                        axis=0
                    )

                    # calculate Macaulay Duration using the aggregated cash flow and yield curve
                    pv_cash_flow = cash_flow_pv(
                        cashflow=aggregated_cash_flow,
                        probabilities=1,
                        discounters=yield_curve,
                    )
                    time_weighted_cash_flow = [
                        t * c for t, c in enumerate(pv_cash_flow, start=0)
                    ]
                    # macaulay_duration = sum(time_weighted_cash_flow) / sum(pv_cash_flow)

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
                    result = {
                        "aggregated_face": mortality_experience["Amount Exposed"][
                            row_range
                        ].sum()
                        * sample_representativeness,
                        "ev": (mortality_experience["lapsed_economic_value"])[
                            row_range
                        ].sum(),
                        "tp_factor": tp_factor,
                        "mort_mult": mort_mult,
                        "premium_markup": premium_markup,
                        "maxle": maxle,
                        "irr": sol.root,
                        # "macaulay": macaulay_duration,
                        "aggregated_cash_flow": aggregated_cash_flow,
                    }

                    print(result)

                    # save result to dict
                    results.append(result)

    with open(DATA_FOLDER / "irr_results_maxle.pickle", "wb") as f:
        pickle.dump(results, f)
