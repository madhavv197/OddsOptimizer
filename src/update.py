import os
import pandas as pd
from thefuzz import process
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.kelly import kelly_criterion
from utils.get_data import get_future_matches, get_past_matches, get_odds
from utils.team_map import get_translation, get_reverse_translation

def check_pending_bets(pending_bets):
    if len(pending_bets) != 0:
        option = str(input(("pending bets not empty, and all entries will be erased if you continue. Continue? (Y/N)")))
        if option.upper() == "Y":
            pass
        else:
            exit()

pd.set_option('display.max_columns', None)

def calculate_ev(prob, odds):
    return prob * (odds - 1) - (1 - prob)

def get_best_match(name, choices, threshold=70):
    best_match, score = process.extractOne(name, choices)
    return best_match if score >= threshold else None

def move_completed_bets(placed_bets, past_bets):
    today = pd.Timestamp.now()
    placed_bets["date"] = pd.to_datetime(placed_bets["date"], format="%d/%m/%Y %H:%M")
    moved_bets = placed_bets[pd.to_datetime(placed_bets["date"]) < today]
    past_bets = pd.concat([past_bets, moved_bets], ignore_index=True)
    placed_bets = placed_bets[~placed_bets.index.isin(moved_bets.index)]
    return placed_bets, past_bets

def calc_past_results(past_matches, past_bets):
    if len(past_bets) == 0:
        return past_bets
    today = pd.Timestamp.now()
    for match in past_matches:
        league = match["league"].lower()

        past_bets["outcome"] = past_bets["outcome"].astype(str)
    
        # Match teams using fuzzy matching
        csv_home_teams = past_bets["home_team"].unique()
        csv_away_teams = past_bets["away_team"].unique()
        all_csv_teams = set(csv_home_teams) | set(csv_away_teams)
        
        matched_home = get_best_match(get_translation(match["home_team"]), all_csv_teams)
        matched_away = get_best_match(get_translation(match["away_team"]), all_csv_teams)
        if matched_home and matched_away:
            one_week_ago = today - pd.Timedelta(days=7)
            past_bets["date"] = pd.to_datetime(past_bets["date"], errors="coerce")
            mask = (past_bets["home_team"] == matched_home) & (past_bets["away_team"] == matched_away) & (past_bets["date"] >= one_week_ago)
            
            #print(f"Before update for {matched_home} vs {matched_away}:\n", past_bets.loc[mask])
    
            past_bets.loc[mask, "home_goals_ft"] = int(match["home_goals"].split()[0])
            past_bets.loc[mask, "away_goals_ft"] = int(match["away_goals"].split()[0])
            past_bets.loc[mask, "outcome"] = str(match["outcome"])
            past_bets.loc[mask, "return"] = past_bets.loc[mask].apply(
            lambda row: row["normalized_risk"] * row[f"odds_{row['bet']}"] if row["bet"] == row["outcome"] else -row["normalized_risk"], axis=1
        )
            
    past_bets = past_bets[["date", "league", "home_team", "away_team", "home_win_%", "draw_%", "away_win_%", 
                           "odds_home", "odds_draw", "odds_away", "bet", "de_normalized_risk", "normalized_risk", "ev", 
                           "home_goals_ft", "away_goals_ft", "outcome", "return"]]
    return past_bets

def add_future_matches(future_matches, pending_bets):
    for match in future_matches:

        home_team = match["home_team"]
        away_team = match["away_team"]

        home_team = get_translation(home_team)
        away_team = get_translation(away_team)
                       
        match_date = match["date"]
        match_league = match["league"]

        home_win_prob = float(str((match["home_win_prob"]).replace("%", "")))/100
        draw_prob = float(str((match["draw_prob"]).replace("%", "")))/100
        away_win_prob = float(str((match["away_win_prob"]).replace("%", "")))/100
        
        new_row = {
            "date": match_date,
            "league": match_league,
            "home_team": home_team,
            "away_team": away_team,
            "home_win_%": home_win_prob,
            "draw_%": draw_prob,
            "away_win_%": away_win_prob,
            "odds_home": None,
            "odds_draw": None,
            "odds_away": None,
            "ev": None,
            "bet": None,
            "de_normalized_risk": None,
            "normalized_risk": None
        }
        pending_bets = pd.concat([pending_bets, pd.DataFrame([new_row])], ignore_index=True)
    return pending_bets

def add_odds(odds_data, pending_bets):
    for odds in odds_data:
        league = odds["league"].lower()
        home_team = odds["home_team"]
        away_team = odds["away_team"]
        win_odds  = odds["win_odds"]
        draw_odds = odds["draw_odds"]
        loss_odds = odds["loss_odds"]

        win_odds = float(win_odds.replace(",", "."))
        draw_odds = float(draw_odds.replace(",", "."))
        loss_odds = float(loss_odds.replace(",", "."))

        pending_bets['odds_home'] = pending_bets['odds_home'].fillna(0)
        pending_bets['odds_draw'] = pending_bets['odds_draw'].fillna(0)
        pending_bets['odds_away'] = pending_bets['odds_away'].fillna(0)

        csv_home_teams = pending_bets["home_team"].unique()
        csv_away_teams = pending_bets["away_team"].unique()
        all_csv_teams = set(csv_home_teams) | set(csv_away_teams)

        matched_home = get_best_match(home_team, all_csv_teams)
        #print(f"found match: {matched_home}")
        matched_away = get_best_match(away_team, all_csv_teams)
        #print(f"found match: {matched_away}")

        #if matched_home is None or matched_away is None:
            #print(f"Skipping {home_team} vs {away_team} due to no match.")

        if matched_home and matched_away:
            # Filter on matching teams
            mask = (pending_bets["home_team"] == matched_home) & (pending_bets["away_team"] == matched_away)


            pending_bets.loc[mask, "odds_home"] = win_odds
            pending_bets.loc[mask, "odds_draw"] = draw_odds
            pending_bets.loc[mask, "odds_away"] = loss_odds

            #print(f"After odds update for {matched_home} vs {matched_away}:\n", pending_bets.loc[mask])

    return pending_bets

def calc_ev_risk(pending_bets, current_balance):
    for idx, row in pending_bets.iterrows():
            p_home = row['home_win_%']
            p_draw = row['draw_%']
            p_away = row['away_win_%']
            
            odds_home = row['odds_home']
            odds_draw = row['odds_draw']
            odds_away = row['odds_away']

            ev_home = 0
            ev_draw = 0
            ev_away = 0
            
            ev_home = calculate_ev(p_home, odds_home)
            #print(f"match: {row["home_team"]} {row["away_team"]} EV : {ev_home}")

            ev_draw = calculate_ev(p_draw, odds_draw)

            #print(f"match: {row["home_team"]} {row["away_team"]} EV : {ev_draw}")

            ev_away = calculate_ev(p_away, odds_away)

            #print(f"match: {row["home_team"]} {row["away_team"]} EV : {ev_away}")
            best_bet = max(ev_home, ev_draw, ev_away)

            if best_bet == ev_home and ev_home > 0:
                risk = current_balance * kelly_criterion(p_home, odds_home, 1)
            elif best_bet == ev_draw and ev_draw > 0:
                risk = current_balance * kelly_criterion(p_draw, odds_draw, 1)
            elif best_bet == ev_away and ev_away > 0:    
                risk = current_balance * kelly_criterion(p_away, odds_away, 1)
            else:
                risk = 0

            pending_bets.loc[idx, 'de_normalized_risk'] = risk
            pending_bets.loc[idx, 'ev'] = best_bet
            if best_bet == ev_home:
                pending_bets.loc[idx, 'bet'] = "home"
            elif best_bet == ev_draw:
                pending_bets.loc[idx, 'bet'] = "draw"
            else:
                pending_bets.loc[idx, 'bet'] = "away"
    return pending_bets



def update_bets(placed_bets, pending_bets, past_bets, future_matches, past_matches, odds_by_league, current_balance, quick_update = False):
    check_pending_bets(pending_bets=pending_bets)
    pending_bets.drop(pending_bets.index, inplace=True)
    
    print("\n")
    print("Moving completed bets from placed bets to past bets...")
    placed_bets, past_bets = move_completed_bets(placed_bets=placed_bets,past_bets=past_bets)

    print("Calculating results for past bets...")
    past_bets = calc_past_results(past_matches=past_matches, past_bets=past_bets)

    if quick_update:
        past_bets.to_csv("data/past_bets.csv", index=False)
        print("Past bets updated.")
        exit()

    print("Compiling data for future matches...")
    pending_bets = add_future_matches(future_matches=future_matches, pending_bets=pending_bets)

    #print(pending_bets)

    pending_bets = add_odds(odds_data=odds_by_league, pending_bets=pending_bets)

    #print(pending_bets)
    
    print("Calculating evs and de-normalized risk...")
    pending_bets = calc_ev_risk(pending_bets, current_balance=current_balance)

    print("\n")

    print("Current pending bets:")

    print("\n")


    print("----------------------------------------------------------------------------------------------------------")

    print("\n")

    print(pending_bets)
    
    save_updated_csvs(pending_bets=pending_bets,past_bets=past_bets)
    


def save_updated_csvs(pending_bets, past_bets):
    pending_bets = pending_bets[pending_bets["ev"] > 0]
    pending_bets.to_csv("data/pending_bets.csv", index=False)
    past_bets.to_csv("data/past_bets.csv", index=False)

    print("CSV files saved successfully.")


if __name__ == "__main__":
    current_placed_bets = pd.read_csv("data/current_placed_bets.csv")
    pending_bets = pd.read_csv("data/pending_bets.csv")
    past_bets = pd.read_csv("data/past_bets.csv")
    #odds_by_league = get_odds()
    #odds_by_league = [] # testing
    future_matches = get_future_matches()
    print(future_matches)
    exit()
    past_matches = get_past_matches()
    update_bets(placed_bets=current_placed_bets,pending_bets=pending_bets, past_bets=past_bets, future_matches=future_matches, past_matches=past_matches, odds_by_league=odds_by_league, current_balance=100)
    