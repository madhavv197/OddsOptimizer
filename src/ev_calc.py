from itertools import combinations
from functools import reduce

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.kelly import kelly_criterion
import ast

def load_matches_from_file(file_path):
    matches = []
    with open(file_path, 'r') as file:
        content = file.read()
        entries = content.split('},')
        for entry in entries:
            if not entry.strip().endswith('}'):
                entry += '}'
            match = ast.literal_eval(entry.strip())
            matches.append(match)
    return matches

def calculate_parlay_ev(parlay):
    total_probability = reduce(lambda x, y: x * y, [outcome['probability'] for outcome in parlay])

    combined_odds = reduce(lambda x, y: x * y, [outcome['odds'] for outcome in parlay])

    profit = (combined_odds - 1)
    
    loss = 1 

    ev = total_probability * profit - (1 - total_probability) * loss
    return ev, total_probability, combined_odds

def generate_outcomes(match):
    return [
        {'fixture': match['fixture'], 'outcome': 'Win', 'probability': match['win_probability'], 'odds': match['win_odds']},
        {'fixture': match['fixture'], 'outcome': 'Draw', 'probability': match['draw_probability'], 'odds': match['draw_odds']},
        {'fixture': match['fixture'], 'outcome': 'Loss', 'probability': match['loss_probability'], 'odds': match['loss_odds']}
    ]

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
            all_parlays.append({'parlay': parlay, 'ev': ev, 'final_probability': probability, 'odds': odds})

    return all_parlays

if __name__ == '__main__':
    matches = load_matches_from_file("data/season2425/matchday21.txt")
    all_parlays = test_all_parlays(matches, max_matches=3)
    sorted_parlays = sorted(all_parlays, key=lambda x: x['ev'], reverse=True)
    filtered_parlays = [parlay for parlay in sorted_parlays if parlay['ev'] > 1 and parlay['final_probability'] > 0.3]
    for i, parlay_data in enumerate(filtered_parlays[:10], start=1):
        parlay_details = [(outcome['fixture'], outcome['outcome']) for outcome in parlay_data['parlay']]
        print(f"Parlay {i}: {parlay_details}, EV: {parlay_data['ev']}, Probability: {parlay_data['final_probability']}, Combined Odds: {parlay_data['odds']}, Kelly: {kelly_criterion(parlay_data['final_probability'], parlay_data['odds'], multiplier=0.15)}")
        print("\n")