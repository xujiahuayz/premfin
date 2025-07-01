# get data from "Universal Life" tab of persistency.xlsx file in DATA_FOLDER, column CE:CF
import pandas as pd
from premiumFinance.constants import DATA_FOLDER
from premiumFinance.insured import Insured
from premiumFinance.inspolicy import InsurancePolicy
from premiumFinance.financing import PolicyFinancingScheme
from premiumFinance.expectedutility import Utility
from premiumFinance.constants import MORTALITY_TABLE_CLEANED_PATH

mortality_experience = pd.read_excel(MORTALITY_TABLE_CLEANED_PATH)

def utility_input(age: int, is_male: bool = False, lapse_assumption: bool = True,
         is_level_premium: bool = True, statutory_interest: float = 0.035,
         premium_markup: float = 0.0, policyholder_rate: float = 0.035,
         cash_interest: float = 0.03, current_vbt: str = "VBT15",
         current_mort: float = 1) -> tuple[float,float,float,float,float]:
    
    issue_age=age-5 
    # select the row in mortality_experience based on issuage, currentage, isMale, and isSmoker
    mortality_experience['mean_face'] = mortality_experience['Amount Exposed'] / mortality_experience['Policies Exposed']
    the_row_face = mortality_experience[
        (mortality_experience["issueage"] == issue_age) &
        (mortality_experience["currentage"] == age) &
        (mortality_experience["isMale"] == is_male) &
        mortality_experience["isSmoker"].isnull()
    ]['mean_face']
    face_value = the_row_face.iloc[0] 
    this_insured = Insured(
        issue_age=issue_age,
        is_male=is_male,
        is_smoker=None,
        current_age=age,
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

    sv = this_financing.surrender_value()
    ev = -this_policy.policy_value(
                issuer_perspective=False,
                at_issue=False,
                discount_rate=policyholder_rate,
            )
    loss = max(sv, ev) 
    mortality = this_insured.mortality_now.conditional_mortality_curve[1]
    premium = this_policy.premium_stream_at_issue[0]
    lapse_rate = 1- this_policy.in_force_rate(assume_lapse=True)[0]
    return loss * face_value, mortality, premium * face_value,lapse_rate, face_value


def final_utility(wealth:float, premium_now: float, 
                  premium_later: float,
                  lapse_rate: float, loss: float, probability_of_loss:float) -> tuple[float,float,float]:
    """
    Calculate the final expected utility of wealth for an insured individual.
    
    Parameters:
    - premium: Insurance premium paid.
    - lapse_rate: Rate at which the insurance policy lapses.
    - loss: Amount lost if the loss occurs.
    
    Returns:
    - Final expected utility of wealth after considering insurance and lapse rate.
    """
    utility = Utility(
        wealth=wealth,
         probability_of_loss=probability_of_loss,
            loss_amount=loss
    )
    return utility.expected_insured_utility_with_insurance(
        premium=premium_now,
        lapse_rate=lapse_rate
    ), utility.expected_insured_utility_with_insurance(
        premium=premium_later,
        lapse_rate=0), utility.expected_insured_utility_without_insurance()


wealth_value = pd.read_excel(
    DATA_FOLDER / "wealth_tables_dy2022.xlsx", sheet_name="Table 5"
    ).iloc[[1, 56, 57,58,59,61,62,63,64], [0,1,18]]
wealth_value.columns = wealth_value.iloc[0]
wealth_value = wealth_value[1:]
# convert  wealth_value['Cash Value Life Insurance']  to numeric, if string then convert to 0
wealth_value['Cash Value Life Insurance'] = pd.to_numeric(
    wealth_value['Cash Value Life Insurance'], errors='coerce').fillna(0)

wealth = pd.read_excel(
    DATA_FOLDER / "wealth_tables_dy2022.xlsx", sheet_name="Table 4"
    ).iloc[[1, 56,57,58,59,61,62,63,64], :11]
# wealth.columns = wealth.iloc[0]
# update wealth columns like wealth.columns[2:] = ['0','2500','7500','17500','37500','75000','175000','375000','750000']
wealth.columns = wealth.iloc[0][:2].to_list() + ['0','2500','7500','17500','37500','75000','175000','375000','750000']
wealth = wealth[1:]

wealth['age'] = [32, 47, 62, 77] * 2
wealth['is_male'] = [True] * 4 + [False] * 4

# scale up number of households
wealth['num_households'] = wealth['Number of Households (thousands)'] * (134100/ wealth['Number of Households (thousands)'].sum()) *1_000 

wealth['cash_life'] = wealth_value['Cash Value Life Insurance']



# for each row in wealth, calculate the loss and mortality
wealth['loss_amount'], wealth['probability_of_loss'], wealth['premium_now'], wealth['lapse_rate'], wealth['face'] = zip(*wealth.apply(
    lambda row: utility_input(
        age=row['age'],
        is_male=row['is_male'],
        lapse_assumption=True
    ), axis=1
)
)

_, _, wealth['premium_later'],_,_ = zip(*wealth.apply(
    lambda row: utility_input(
        age=row['age'],
        is_male=row['is_male'],
        lapse_assumption=False
    ), axis=1
)
)

# make age, is_male ... until the last column index columns of the wealth dataframe
wealth = wealth.drop(columns=['Characteristic', 'Number of Households (thousands)'])
# make index
wealth.set_index(['age', 'is_male', 'num_households', 'cash_life', 'loss_amount', 'probability_of_loss', 'premium_now', 'premium_later', 'lapse_rate', 'face'], inplace=True)
row_num = wealth.shape[0]

wealth_long = wealth.stack().reset_index()
wealth_long.rename(columns={
    'level_10': 'wealth', 
    0: 'households_in_bin'
}, inplace=True)

wealth_long['wealth'] = pd.to_numeric(wealth_long['wealth'], errors='coerce').fillna(0)



wealth_long['utility_ins_before'], wealth_long['utility_ins_after'], wealth_long['utility_no_ins']  = zip(*wealth_long.apply(
    lambda row: final_utility(
        wealth=row['wealth'],
        premium_now=row['premium_now'],
        premium_later=row['premium_later'],
        lapse_rate=row['lapse_rate'],
        loss=row['loss_amount'],
        probability_of_loss=row['probability_of_loss']
    ), axis=1
))