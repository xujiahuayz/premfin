# import figure folder
from premiumFinance.constants import FIGURE_FOLDER
from premiumFinance.financing import PolicyFinancingScheme, yield_curve
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.insured import Insured

current_vbt: str = "VBT15"
current_mort: float = 1
is_level_premium=True
policyholder_rate=yield_curve
statutory_interest: float = 0.035
premium_markup: float = 0.0
cash_interest: float = 0.03
premium_hike: float = 0.0
issue_age = 35
# current_age = issue_age

for lapse_assumption in [True, False]:
    this_insured = Insured(
        issue_age=issue_age,
        is_male=False,
        is_smoker=False,
        current_age=issue_age,
        issue_vbt="VBT01",
        current_vbt=current_vbt,
        current_mortality_factor=current_mort,
    )

    # premium markup = 0 for default case to calculate
    this_policy = InsurancePolicy(
        insured=this_insured,
        lapse_assumption=lapse_assumption,
        is_level_premium=is_level_premium,
        statutory_interest=statutory_interest,
        premium_markup=premium_markup,
        policyholder_rate=policyholder_rate,
        cash_interest=cash_interest,
    )
    this_financing = PolicyFinancingScheme(policy=this_policy)


    sv_values = []
    ev_values = []
    age_values = []
    offered_values = []
    while this_insured.current_age < 100:
        age_values.append(this_insured.current_age)

        sv = this_financing.surrender_value()
        ev = -this_policy.policy_value(
                    issuer_perspective=False,
                    at_issue=False,
                    discount_rate=policyholder_rate,
                )

        sv_values.append(sv)
        ev_values.append(ev)

        # the offered value is the max of the surrender value and the economic value
        offered_values.append(max(sv, ev))


        this_insured.current_age += 1

    # plot sv and ev

    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.plot(age_values, sv_values, label="Surrender Value", linestyle=":", alpha=0.5, linewidth=6)
    plt.plot(age_values, ev_values, label="Economic Value", linestyle=":", alpha=0.5, linewidth=6)
    plt.plot(age_values, offered_values, label="Offered Value", color="red")
    # horizontal line at 0
    plt.axhline(0, color="black", linestyle="--")
    plt.xlabel("Age")
    plt.ylabel("Value as a fraction of face amount")
    plt.title("Surrender Value and Economic Value")
    plt.legend()
    # save to pdf
    plt.savefig(
        FIGURE_FOLDER / f"sv_ev_{lapse_assumption}.pdf",
        bbox_inches="tight",
    )
    plt.show()
