import numpy as np
import os
import sys
from collections import defaultdict
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
np.set_printoptions(precision=10, suppress=False)
from src.ev_calc import test_all_parlays
from utils.loader import load_matches_from_folder
from utils.kelly import kelly_criterion

def get_data_from_matchdays(matchday_data):
    """
    Extract probabilities and odds for each parlay size from matchday data.
    """
    probabilities = []
    odds = []
    evs_dict = defaultdict(list)
    kellys_dict = defaultdict(list)
    for matchday in matchday_data:
        for parlay_size in range(1, 11):
            parlays = test_all_parlays(matches=matchday, max_matches=parlay_size)
            if parlays:
                choice = parlays[0]
                probabilities.append({'parlay_size': parlay_size, 'probability': choice['final_probability']})
                odds.append({'parlay_size': parlay_size, 'odds': choice['odds']})
                evs_dict[parlay_size].append(choice['ev'])
                kellys_dict[parlay_size].append(
                    kelly_criterion(choice['final_probability'], choice['odds'], multiplier=0.15)
                )

    return probabilities, odds, evs_dict, kellys_dict


def filter_data_with_discrepancy(data, key, threshold=1.0):

    min_val = min(data, key=lambda x: x[key])[key]
    max_val = max(data, key=lambda x: x[key])[key]
    mean_val = np.mean([entry[key] for entry in data])
    normalized_range = (max_val - min_val) / mean_val if mean_val != 0 else 0

    if normalized_range <= threshold:
       return data
    if key == 'probability':
        filtered_data = [entry for entry in data if min_val < entry[key] <= max_val]
    else:
        filtered_data = [entry for entry in data if min_val <= entry[key] < max_val]
    return filtered_data

def create_strata(data, key, num_bins=50, threshold=1.0):

    grouped_data = defaultdict(list)
    for entry in data:
        grouped_data[entry['parlay_size']].append(entry)

    strata = {}
    for parlay_size, entries in grouped_data.items():
        #filter
        entries = filter_data_with_discrepancy(entries, key, threshold)

        values = [entry[key] for entry in entries]
        min_val, max_val = min(values), max(values)

        if max_val - min_val < num_bins:
            bins = np.linspace(min_val, max_val + 1e-3, num_bins + 1)
        else:
            bins = np.linspace(min_val, max_val, num_bins + 1)

        binned_data = {f"{bins[i]:.2f}-{bins[i+1]:.2f}": [] for i in range(len(bins) - 1)}

        for value in values:
            for i in range(len(bins) - 1):
                if bins[i] <= value < bins[i + 1]:
                    binned_data[f"{bins[i]:.2f}-{bins[i+1]:.2f}"].append(value)
                    break

        if max_val == bins[-1]:
            binned_data[f"{bins[-2]:.2f}-{bins[-1]:.2f}"].append(max_val)

        print(f'{key} binned data: ', binned_data)

        strata[parlay_size] = binned_data

    return strata

def get_probability_strata(probabilities, num_bins=50, threshold=1.0):

    return create_strata(probabilities, 'probability', num_bins, threshold)

def get_odds_strata(odds, num_bins=50, threshold=1.0):

    return create_strata(odds, 'odds', num_bins, threshold)

def get_all_strata(probabilities, odds, prob_num_bins=50, odds_num_bins=50):
    prob_strata = get_probability_strata(probabilities, num_bins=prob_num_bins)
    odds_strata = get_odds_strata(odds, num_bins=odds_num_bins)
    return prob_strata, odds_strata

def stratified_sampling(strata, parlay_size, num_samples):
    strata_data = strata.get(parlay_size, {})
    total_values = sum(len(values) for values in strata_data.values())
    samples = []
    for bin_range, values in strata_data.items():
        if not values:
            continue
        
        bin_edges = list(map(float, bin_range.split('-')))
        bin_low, bin_high = bin_edges
        proportion = len(values) / total_values
        bin_samples = round(proportion * num_samples)
        samples.extend(np.random.uniform(bin_low, bin_high, bin_samples))

    return samples

def get_other_metrics(metric_dict, parlay_size):
    return metric_dict.get(parlay_size, [])

if __name__ == "__main__":
    prob_strata, odds_strata = get_all_strata(0.1,50)  

    # Print example strata
    print("Probability Strata:", prob_strata)
    print("Odds Strata:", odds_strata)
