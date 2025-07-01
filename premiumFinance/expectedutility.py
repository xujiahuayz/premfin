import numpy as np


class Utility:
    """
    A class to represent utility functions for insured individuals.
    """

    def __init__(self, wealth: float = 0.0, probability_of_loss: float = 0.0, loss_amount: float = 0.0) -> None:
        """
        Initialize the Utility class.
        This class does not require any parameters for initialization.
        """

        if wealth < 0 or loss_amount < 0:
            raise ValueError("Wealth, and loss amount must be non-negative.")
    
        if probability_of_loss < 0 or probability_of_loss > 1:
            raise ValueError("Probability of loss must be between 0 and 1.")
        
        self.wealth = wealth
        self.probability_of_loss = probability_of_loss
        self.loss_amount = loss_amount
        

    @staticmethod
    def insured_utility(wealth: float) -> float:
        """
        Calculate the utility of wealth for an insured individual.
        The utility is a simple logarithmic function of wealth.
        """
        wealth = max(wealth, 0)  # Avoid log(0) or negative wealth 
        return np.log(wealth)


    def expected_insured_utility_without_insurance(
        self
    ) -> float:
        """
        Calculate the expected utility of wealth for an insured individual without insurance.
        
        Returns:
        - Expected utility of wealth without insurance.
        """
        wealth = self.wealth
        probability_of_loss = self.probability_of_loss
        loss_amount = self.loss_amount

        expected_utility = (
            (1 - probability_of_loss) * self.insured_utility(wealth)
            + probability_of_loss * self.insured_utility(wealth - loss_amount)
        )

        return expected_utility
    
    def expected_insured_utility_full_insurance(
        self,
        premium: float
    ) -> float:
        """
        Calculate the expected utility of wealth for an insured individual with full insurance.
        
        Parameters:
        - wealth: Initial wealth of the individual.
        - premium: Insurance premium paid.
        
        Returns:
        - Expected utility of wealth after considering full insurance.
        """
        wealth = self.wealth

        expected_utility = self.insured_utility(wealth - premium)

        return expected_utility

    def expected_insured_utility_with_insurance(
        self,
        premium: float,
        lapse_rate: float
    ) -> float:
        """
        Calculate the expected utility of wealth for an insured individual over one period.
        
        Parameters:
        - wealth: Initial wealth of the individual.
        - premium: Insurance premium paid.
        - probability_of_loss: Probability of a loss occurring.
        - loss_amount: Amount lost if the loss occurs.
        
        Returns:
        - Expected utility of wealth after considering insurance.
        """

        excepted_utility = (1-lapse_rate) * self.expected_insured_utility_full_insurance(premium) + lapse_rate * self.expected_insured_utility_without_insurance()

        return excepted_utility
    
    def final_expected_utility(
        self,
        premium: float,
        lapse_rate: float
    ) -> float:
        """
        Calculate the final expected utility of wealth for an insured individual.
        
        Parameters:
        - premium: Insurance premium paid.
        - lapse_rate: Rate at which the insurance policy lapses.
        
        Returns:
        - Final expected utility of wealth after considering insurance and lapse rate.
        """
        return max(
            self.expected_insured_utility_with_insurance(premium, lapse_rate),
            self.expected_insured_utility_without_insurance()
        )

if __name__ == "__main__":
    # Example usage
    utility = Utility(wealth=100000, probability_of_loss=0.001, loss_amount=50000)
    print("Expected utility with insurance:", utility.expected_insured_utility_with_insurance(premium=100, lapse_rate=0))
    print("Expected utility without insurance:", utility.expected_insured_utility_without_insurance())
    print("Utility of wealth:", utility.insured_utility(wealth=100000))    