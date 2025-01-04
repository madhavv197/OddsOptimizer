from itertools import combinations, product
from tqdm import tqdm
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.kelly import kelly_criterion
from utils.loader import generate_outcomes, load_matches_from_file
from utils.calc_ev_from_prob import calculate_parlay_ev

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


def validate_parlay_counts(parlay_counts):
    """
    Validates that the total number of parlays adds up to 10.
    """
    if sum(key*value for key, value in parlay_counts.items()) > 10:
        raise ValueError("The total number of parlays must add up to 10.")


def find_best_parlay_combinations_with_custom_counts(matches, parlay_counts):
    """
    Finds the best combinations of parlays based on user-specified counts.

    Args:
        matches: List of match data.
        parlay_counts: Dictionary specifying the number of parlays for each size.

    Returns:
        List of parlay combinations with the highest EV.
    """
    # Validate input
    validate_parlay_counts(parlay_counts)

    # Generate all outcomes
    all_outcomes = [generate_outcomes(match) for match in matches]

    # Generate parlays by size
    parlays_by_size = {size: [] for size in parlay_counts.keys()}
    for size in parlay_counts.keys():
        for outcome_combination in combinations(
            [outcome for match_outcomes in all_outcomes for outcome in match_outcomes], size
        ):
            if len(set([outcome['fixture'] for outcome in outcome_combination])) == size:
                parlay = list(outcome_combination)
                ev, probability, odds = calculate_parlay_ev(parlay)
                if ev > 0:  # Only include positive EV parlays
                    count_divisor = parlay_counts.get(size, 1)
                    if count_divisor !=0:
                        kelly_value = kelly_criterion(probability, odds, 0.15) / count_divisor
                    else: 
                        kelly_value = 0
                    parlays_by_size[size].append({
                        'parlay': parlay,
                        'ev': ev,
                        'final_probability': probability,
                        'odds': odds,
                        'matches': {outcome['fixture'] for outcome in parlay},
                        'kelly': kelly_value
                    })

    for size, count in parlay_counts.items():
        if len(parlays_by_size[size]) < count:
            raise ValueError(f"Not enough valid parlays of size {size} to fulfill the request.")

    size_combinations = []
    for size, count in parlay_counts.items():
        size_combinations.append(list(combinations(parlays_by_size[size], count)))

    all_combinations = product(*size_combinations)

    best_combinations = []
    total_combinations = 1
    for size_comb in size_combinations:
        total_combinations *= len(size_comb)

    with tqdm(total=total_combinations, desc="Evaluating combinations") as progress_bar:
        for combination in all_combinations:
            flattened_combination = [parlay for subset in combination for parlay in subset]
            combined_matches = set.union(*[parlay['matches'] for parlay in flattened_combination])
            
            if len(combined_matches) == sum(len(parlay['matches']) for parlay in flattened_combination):
                total_ev = sum(parlay['ev'] for parlay in flattened_combination)
                best_combinations.append({
                    'combination': flattened_combination,
                    'total_ev': total_ev
                })
            progress_bar.update(1)

    best_combinations.sort(key=lambda x: x['total_ev'], reverse=True)

    return best_combinations


if __name__ == '__main__':
    matches = load_matches_from_file("data/season2425/matchday16.txt")

    parlays = test_all_parlays(matches, max_matches= 3)

    for i, parlay_data in enumerate(parlays[:10], start=1):
        parlay_details = [(outcome['fixture'], outcome['outcome']) for outcome in parlay_data['parlay']]
        print(f"Parlay {i}: {parlay_details}, EV: {parlay_data['ev']}, Probability: {parlay_data['final_probability']}, Combined Odds: {parlay_data['odds']}, Kelly: {kelly_criterion(parlay_data['final_probability'], parlay_data['odds'], multiplier=0.15)}, Metric: {parlay_data['metric']}")
        print("\n")

    parlay_counts = {
        1: 6,
        2: 2,
        3: 0,
        4: 0 
    }

    best_combinations = find_best_parlay_combinations_with_custom_counts(matches, parlay_counts)

    # Print the top 5 combinations
    for i, combination_data in enumerate(best_combinations[:5], start=1):
        print(f"Combination {i}:")
        for parlay_data in combination_data['combination']:
            parlay_details = [(outcome['fixture'], outcome['outcome']) for outcome in parlay_data['parlay']]
            print(f"  Parlay: {parlay_details}, EV: {parlay_data['ev']}, Combined Odds: {parlay_data['odds']}, Probability: {parlay_data['final_probability']}, Kelly: {parlay_data['kelly']}")
        print(f"  Total EV: {combination_data['total_ev']}\n")
