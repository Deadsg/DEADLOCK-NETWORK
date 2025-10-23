import numpy as np

class RewardEngine:
    """
    Calculates rewards and adjusts emission rates based on DQN principles.
    """

    def __init__(self, alpha=0.7, gamma=0.9, lambda_decay=0.05, epsilon=1e-6):
        """
        Initializes the RewardEngine.

        Args:
            alpha (float): Learning rate.
            gamma (float): Discount factor for future rewards.
            lambda_decay (float): Decay factor for emission rate.
            epsilon (float): Small value to avoid division by zero.
        """
        self.alpha = alpha
        self.gamma = gamma
        self.lambda_decay = lambda_decay
        self.epsilon = epsilon

    def calculate_reward(self, mining_effort, difficulty):
        """
        Calculates the reward for a mining action.

        Args:
            mining_effort (float): The effort spent by the miner.
            difficulty (float): The current mining difficulty.

        Returns:
            float: The calculated reward.
        """
        return mining_effort / (difficulty + self.epsilon)

    def adjust_emission_rate(self, current_emission_rate, q_avg, q_max):
        """
        Adjusts the emission rate based on the average and max Q-values.

        Args:
            current_emission_rate (float): The current emission rate.
            q_avg (float): The average Q-value.
            q_max (float): The maximum Q-value.

        Returns:
            float: The adjusted emission rate.
        """
        if q_max > 0:
            return current_emission_rate * (1 - self.lambda_decay * (q_avg / q_max))
        else:
            return current_emission_rate
