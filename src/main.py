import executor
import update
import pandas as pd

def main():
    current_placed_bets = pd.read_csv("data/current_placed_bets.csv")
    pending_bets = pd.read_csv("data/pending_bets.csv")
    past_bets = pd.read_csv("data/past_bets.csv")

    odds_by_league = update.get_odds()
    future_matches = update.get_future_matches()
    past_matches = update.get_past_matches()

    update.update_bets(placed_bets=current_placed_bets,pending_bets=pending_bets, past_bets=past_bets, future_matches=future_matches, past_matches=past_matches, odds_by_league=odds_by_league, current_balance=100)
    
    pending_bets = pd.read_csv("data/pending_bets.csv")
    username = "madhavv197@gmail.com"
    password = "vIjay007007!"

    executor.place_all_pending_bets(pending_bets=pending_bets, username=username, password=password)

if __name__ == "__main__":
    main()