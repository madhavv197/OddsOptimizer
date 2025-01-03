from functools import reduce
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

def calculate_parlay_ev(parlay):
    total_probability = reduce(lambda x, y: x * y, [outcome['probability'] for outcome in parlay])

    combined_odds = reduce(lambda x, y: x * y, [outcome['odds'] for outcome in parlay])

    profit = (combined_odds - 1)
    
    loss = 1 

    ev = total_probability * profit - (1 - total_probability) * loss
    return ev, total_probability, combined_odds

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

    sorted_parlays = sorted(all_parlays, key=lambda x: x['metric'], reverse=True)
    filtered_parlays = [parlay for parlay in sorted_parlays if parlay['ev'] > 0.3]

    return filtered_parlays

if __name__ == '__main__':
    ev = calculate_parlay_ev(parlay)