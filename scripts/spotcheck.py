    from premiumFinance.insured import Insured
    from premiumFinance.inspolicy import InsurancePolicy
    
    import itertools 


    # check against: https://www.forbes.com/advisor/life-insurance/universal-life-insurance/
    def spot_check_premium(lapse_assumption: bool, gender: bool, age: int):
        insrd_benchmark = Insured(
            issue_age=age,
            is_male=gender,
            is_smoker=False,
            current_age=age,
            issue_mortality_factor=1.0,
            current_mortality_factor=1.0,
            issue_vbt="VBT01",
            current_vbt="VBT15",
        )

        insPol = InsurancePolicy(
            insured=insrd_benchmark,
            is_level_premium=True,
            lapse_assumption=lapse_assumption,
        )

        print(
            f"gender: {'Male' if gender else 'Female'}\n policy lapse: {lapse_assumption}\n age: {age}\n premium: {insPol._level_premium}"
        )


    if __name__ == "__main__":
        # for (lapse_assumption, gender, age) in zip(
        #     [True, False], [True, False], [30, 35, 40, 45, 50, 55, 60]
        # ):
        #     spot_check_premium(lapse_assumption=lapse_assumption, gender=gender, age=age)
        for lapse_assumption, gender, age in itertools.product(
            [True, False], [True, False], [30, 35, 40, 45, 50, 55, 60]
        ):
            spot_check_premium(lapse_assumption=lapse_assumption, gender=gender, age=age)
