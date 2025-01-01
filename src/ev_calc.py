from itertools import combinations
from functools import reduce

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.kelly import kelly_criterion
matches = [
    {'fixture': 'Tottenham vs Newcastle', 'win_probability': 0.45, 'draw_probability': 0.22, 'loss_probability': 0.33, 'win_odds': 2.9, 'draw_odds': 3.85, 'loss_odds': 2.23},
    {'fixture': 'Bournemouth vs Everton', 'win_probability': 0.54, 'draw_probability': 0.22, 'loss_probability': 0.24, 'win_odds': 1.76, 'draw_odds': 3.85, 'loss_odds': 4.5},
    {'fixture': 'Aston Villa vs Leicester City', 'win_probability': 0.75, 'draw_probability': 0.17, 'loss_probability': 0.08, 'win_odds': 1.34, 'draw_odds': 5.5, 'loss_odds': 8.5},
    {'fixture': 'Crystal Palace vs Chelsea', 'win_probability': 0.25, 'draw_probability': 0.23, 'loss_probability': 0.52, 'win_odds': 3.85, 'draw_odds': 3.8, 'loss_odds': 1.9},
    {'fixture': 'Southampton vs Brentford', 'win_probability': 0.31, 'draw_probability': 0.28, 'loss_probability': 0.41, 'win_odds': 2.7, 'draw_odds': 3.45, 'loss_odds': 2.54},
    {'fixture': 'Man City vs West Ham', 'win_probability': 0.76, 'draw_probability': 0.15, 'loss_probability': 0.09, 'win_odds': 1.31, 'draw_odds': 6.0, 'loss_odds': 8.0},
    {'fixture': 'Brighton vs Arsenal', 'win_probability': 0.17, 'draw_probability': 0.21, 'loss_probability': 0.61, 'win_odds': 4.25, 'draw_odds': 3.85, 'loss_odds': 1.78},
    {'fixture': 'Fulham vs Ipswich Town', 'win_probability': 0.69, 'draw_probability': 0.19, 'loss_probability': 0.12, 'win_odds': 1.56, 'draw_odds': 4.25, 'loss_odds': 5.75},
    {'fixture': 'Liverpool vs Man United', 'win_probability': 1, 'draw_probability': 0, 'loss_probability': 0, 'win_odds': 1.24, 'draw_odds': 6.25, 'loss_odds': 9.25},
    {'fixture': 'Wolves vs Nottingham Forest', 'win_probability': 0.1, 'draw_probability': 0.27, 'loss_probability': 0.63, 'win_odds': 3, 'draw_odds': 3.35, 'loss_odds': 2.37}
]

stake = 1

def calculate_parlay_ev(parlay):
    total_probability = reduce(lambda x, y: x * y, [outcome['probability'] for outcome in parlay])

    combined_odds = reduce(lambda x, y: x * y, [outcome['odds'] for outcome in parlay])

    profit = stake * (combined_odds - 1)
    
    loss = stake 

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
            all_parlays.append({'parlay': parlay, 'ev': ev, 'final_probability': probability, 'odds': odds, 'ratio': (probability * 1000) / odds})

    return all_parlays

if __name__ == '__main__':
    all_parlays = test_all_parlays(matches, max_matches=3)
    sorted_parlays = sorted(all_parlays, key=lambda x: x['ev'], reverse=True)
    filtered_parlays = [parlay for parlay in sorted_parlays if parlay['ev'] > 1 and parlay['final_probability'] > 0.3]


    for i, parlay_data in enumerate(filtered_parlays[:10], start=1):
        parlay_details = [(outcome['fixture'], outcome['outcome']) for outcome in parlay_data['parlay']]
        print(f"Parlay {i}: {parlay_details}, EV: {parlay_data['ev']}, Probability: {parlay_data['final_probability']}, Combined Odds: {parlay_data['odds']}, Ratio: {parlay_data['ratio']}, Kelly: {kelly_criterion(parlay_data['final_probability'], parlay_data['odds'], multiplier=0.15)}")
        print("\n")