import sys
import os
from itertools import combinations
from tqdm import tqdm
from collections import defaultdict
import re

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.kelly import kelly_criterion
from utils.loader import generate_outcomes, load_matches_from_files, load_matches_from_file
from utils.calc_ev_from_prob import calculate_parlay_ev

def generate_outcomes(match, league_prefix):
    return [
        {'fixture': f"{league_prefix}_{match['fixture']}", 'outcome': 'Win', 'probability': match['win_probability'], 'odds': match['win_odds']},
        {'fixture': f"{league_prefix}_{match['fixture']}", 'outcome': 'Draw', 'probability': match['draw_probability'], 'odds': match['draw_odds']},
        {'fixture': f"{league_prefix}_{match['fixture']}", 'outcome': 'Loss', 'probability': match['loss_probability'], 'odds': match['loss_odds']}
    ]

def test_all_parlays(matches, max_matches=None):
    all_parlays = []
    all_outcomes = [generate_outcomes(match, match['league_prefix']) for match in matches]
    match_count = len(matches) if max_matches is None else max_matches

    for outcome_combination in combinations(
        [outcome for match_outcomes in all_outcomes for outcome in match_outcomes],
        match_count
    ):
        if len(set([outcome['fixture'] for outcome in outcome_combination])) == match_count:
            parlay = list(outcome_combination)
            ev, probability, odds = calculate_parlay_ev(parlay)
            if ev > 0:
                all_parlays.append({
                    'parlay': parlay,
                    'ev': ev,
                    'final_probability': probability,
                    'odds': odds
                })

    sorted_parlays = sorted(all_parlays, key=lambda x: x['ev'], reverse=True)
    return sorted_parlays

def total_kelly_risk(bets, multiplier=1.0, bank_size=20):
    total = 0.0
    for b in bets:
        prob = b['final_probability']
        odds = b['odds']
        kelly_fraction = kelly_criterion(prob, odds, multiplier=multiplier)
        stake = bank_size * kelly_fraction
        total += stake
    return total

def find_best_multiplier(bets, max_risk=20.0, step=0.01):
    multiplier = 1.0
    while multiplier >= 0.0:
        risk = total_kelly_risk(bets, multiplier=multiplier, bank_size=max_risk)
        if risk <= max_risk:
            return multiplier, risk
        multiplier -= step
    return 0.0, 0.0

def filter_highest_probability_bets(single_bets):
    highest_bets = {}
    
    for bet in single_bets:
        outcome = bet['parlay'][0] 
        fixture = outcome['fixture']
        
        if bet['ev'] > 0:
            if fixture not in highest_bets or outcome['probability'] > highest_bets[fixture]['parlay'][0]['probability']:
                highest_bets[fixture] = bet

    # Return the bets as a list
    return list(highest_bets.values())



if __name__ == '__main__':
    # match_files = [
    #     "data/bun_season2425/matchday_19.txt",
    #     "data/cha_season2425/matchday_29.txt",
    #     "data/leo_season2425/matchday_28.txt",
    #     "data/let_season2425/matchday_28.txt",
    #     "data/ll_season2425/matchday_21.txt",
    #     "data/fl_season2425/matchday_19.txt",
    #     "data/pl_season2425/matchday_23.txt",
    #     "data/sea_season2425/matchday_22.txt"
    # ]

    match_files = [
                   "data/ucl_season2425/matchday_8.txt",
                   "data/let_season2425/matchday_29.txt",
                   "data/uel_season2425/matchday_8.txt",
                   "data/leo_season2425/matchday_29.txt"]
    #
    current_capital = 54

    league_mapping = {
        "bun": "Bundesliga",
        "cha": "Championship",
        "leo": "League One",
        "let": "League Two",
        "ll": "La Liga",
        "fl": "Ligue 1",
        "pl": "Premier League",
        "sea": "Serie A",
        "ucl": "UEFA Champions League",
        "uel": "UEFA Europa League"
    }

    pattern = r"data/([a-z]{2,3})_season"

    all_matches = []
    for match_file in match_files:
        league_code = re.search(pattern, match_file).group(1)
        league_prefix = league_mapping.get(league_code, "Unknown League")
        matches = load_matches_from_files([match_file])
        for match in matches:
            match['league_prefix'] = league_code
        all_matches.extend(matches)
    single_bets = test_all_parlays(all_matches, max_matches=1)
    unique_bets = filter_highest_probability_bets(single_bets)

    total_risk = total_kelly_risk(single_bets)
 
    best_multiplier, final_risk = find_best_multiplier(unique_bets, max_risk=current_capital*0.8*(len(unique_bets)/55), step=0.01)

    bets_by_league = defaultdict(list)
    print("\n")
    print("==========================================")
    print("\n")

    for bet in unique_bets:
        fixture = bet['parlay'][0]['fixture']
        league_code = fixture.split('_')[0]
        league = league_mapping.get(league_code, "Unknown League")
        bets_by_league[league].append(bet)

    for league, bets in sorted(bets_by_league.items()):
        print(f"League: {league}")
        print(f"{'#':<3}{'Fixture':<50}{'Outcome':<10}{'EV':<10}{'Probability':<12}{'Odds':<10}{'Kelly Stake':<10}")
        print("-" * 80)
        for i, bet in enumerate(bets, start=1):
            fixture = bet['parlay'][0]['fixture'].split('_')[1]
            outcome = bet['parlay'][0]['outcome']
            ev = bet['ev']
            probability = bet['final_probability']
            odds = bet['odds']
            kelly_fraction = kelly_criterion(probability, odds, multiplier=best_multiplier)
            kelly_stake = current_capital*0.8*(len(unique_bets)/55) * kelly_fraction

            print(f"{i:<3}{fixture:<50}{outcome:<10}{ev:<10.4f}{probability:<12.4f}{odds:<10.2f}{kelly_stake:<10.2f}")

        print("\n")

    print("\n==========================================")
    print(f"Best Multiplier Found: {best_multiplier:.2f}")
    print(f"Max Allowable Risk {current_capital*0.8*(len(unique_bets)/55)}")
    print(f"Total Risk: {final_risk:.2f}")
    print("==========================================\n")
