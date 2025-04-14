import pandas as pd
import numpy as np

def get_sharpe(past_bets):
    past_bets["relative_return"] = np.where(past_bets["return"] > 0, past_bets["return"] - past_bets["normalized_risk"], past_bets["return"]) / past_bets["normalized_risk"]

    sharpe_ratio_per_bet = past_bets["relative_return"].mean() / past_bets["relative_return"].std()
    return sharpe_ratio_per_bet * (2400)**0.5

if __name__ == "__main__":
    past_bets = pd.read_csv("data/past_bets.csv")
    print(get_sharpe(past_bets))