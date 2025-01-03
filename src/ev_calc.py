from itertools import combinations

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.kelly import kelly_criterion
from utils.loader import generate_outcomes, load_matches_from_file
from utils.calc_ev_from_prob import calculate_parlay_ev, test_all_parlays
import ast

def test_all_parlays(matches, max_matches=None):
    """
    Generate all possible parlays, restricting to max_matches if specified.
    """
    all_parlays = []

    all_outcomes = [generate_outcomes(match) for match in matches]
    match_count = len(matches) if max_matches is None else max_matches

    for outcome_combination in combinations([outcome for match_outcomes in all_outcomes for outcome in match_outcomes], match_count):
        if len(set([outcome['fixture'] for outcome in outcome_combination])) == match_count:
            parlay = list(outcome_combination)
            ev, probability, odds = calculate_parlay_ev(parlay)
            all_parlays.append({'parlay': parlay, 'ev': ev, 'final_probability': probability, 'odds': odds, 'metric': 0.25*ev+0.75*probability})

    sorted_parlays = sorted(all_parlays, key=lambda x: x['ev'], reverse=True)
    filtered_parlays = [parlay for parlay in sorted_parlays if parlay['ev'] > 0]

    return filtered_parlays

if __name__ == '__main__':
    matches = load_matches_from_file("data/season2425/matchday19.txt")
    parlays = test_all_parlays(matches, max_matches= 3)

    for i, parlay_data in enumerate(parlays[:10], start=1):
        parlay_details = [(outcome['fixture'], outcome['outcome']) for outcome in parlay_data['parlay']]
        print(f"Parlay {i}: {parlay_details}, EV: {parlay_data['ev']}, Probability: {parlay_data['final_probability']}, Combined Odds: {parlay_data['odds']}, Kelly: {kelly_criterion(parlay_data['final_probability'], parlay_data['odds'], multiplier=0.15)}, Metric: {parlay_data['metric']}")
        print("\n")