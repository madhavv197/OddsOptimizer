import random
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.loader import load_matches_from_folder
from utils.get_strata import get_all_strata, stratified_sampling, get_data_from_matchdays, get_other_metrics

random.seed(0)

def simulate_matchday(odds, prob, stake=None):
    if stake is None:
        stake = (starting_capital*0.15*(odds*prob-(1-prob)))/odds
        stake = max(stake,0.01)
    if random.random() < prob:
        return stake*(odds - 1)  # Profit if the parlay hits
    else:
        return stake*(-1)  # Loss if the parlay misses

def monte_carlo_simulation(prob_strata, odds_strata, starting_capital, max_parlay_size, num_simulations=38):

    total_profit = 0
    cumulative_returns = [starting_capital]
    profits = []

    max_drawdown = 0
    peak = starting_capital

    for i in range(num_simulations):
        prob, odds  = prob_strata[i], odds_strata[i]
        profit = simulate_matchday(odds, prob)
        profits.append(profit)
        total_profit += profit
        current_balance = starting_capital + total_profit
        if current_balance <= 0:
            break
        cumulative_returns.append(current_balance)

        peak = max(peak, current_balance)
        if current_balance < starting_capital:
            drawdown = (current_balance-starting_capital) / starting_capital
            max_drawdown = max(abs(max_drawdown), abs(drawdown))

    average_profit = total_profit / num_simulations
    hit_rate = len([p for p in profits if p > 0]) / num_simulations
    std_dev = np.std(profits)
    std_dev = max(std_dev, 1)

    sharpe_ratio = average_profit / std_dev

    return {
        'average_profit': average_profit,
        'hit_rate': hit_rate,
        'total_profit': total_profit,
        'num_simulations': num_simulations,
        'std_dev': std_dev,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'cumulative_returns': cumulative_returns
    }

def simulate_combination_matchday(custom_metric, starting_capital):
    profit = 0
    metrics = custom_metric['metrics']
    
    for parlay_size in metrics:
        median_prob = parlay_size['median_probability']
        median_odds = parlay_size['median_odds']
        median_kelly = parlay_size['median_kelly']
        profit += simulate_matchday(median_odds, median_prob, median_kelly*starting_capital)
    return profit


def combination_monte_carlo_simulation(starting_capital, custom_metrics, num_simulations=38):
    total_profit = 0
    cumulative_returns = [starting_capital]
    profits = []

    max_drawdown = 0
    peak = starting_capital

    for i in range(num_simulations):
        profit = simulate_combination_matchday(custom_metrics, starting_capital)
        profits.append(profit)
        total_profit += profit
        current_balance = starting_capital + total_profit
        if current_balance <= 0:
            break
        cumulative_returns.append(current_balance)

        peak = max(peak, current_balance)
        if current_balance < starting_capital:
            drawdown = (current_balance-starting_capital) / starting_capital
            max_drawdown = max(abs(max_drawdown), abs(drawdown))

    average_profit = total_profit / num_simulations
    hit_rate = len([p for p in profits if p > 0]) / num_simulations
    std_dev = np.std(profits)
    std_dev = max(std_dev, 1)

    sharpe_ratio = average_profit / std_dev

    return {
        'average_profit': average_profit,
        'hit_rate': hit_rate,
        'total_profit': total_profit,
        'num_simulations': num_simulations,
        'std_dev': std_dev,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'cumulative_returns': cumulative_returns
    }

def multi_seed_combination_average(custom_metrics, starting_capital, num_seeds = 5, num_simulations=38):
    aggregated_results = {
        'average_ev': 0,
        'average_stake': 0,
        'average_profit': 0,
        'hit_rate': 0,
        'total_profit': 0,
        'std_dev': 0,
        'sharpe_ratio': 0,
        'max_drawdown': 0,
        'cumulative_returns': []
    }
    evs = []
    stakes = []
    for metric in custom_metrics['metrics']:
        stakes.append(metric['median_kelly'])
        evs.append(metric['median_ev'])
    aggregated_results['average_ev'] = np.mean(np.array(evs))
    aggregated_results['average_stake'] = np.mean(np.array(stakes))

    for seed in range(num_seeds):
        np.random.seed(seed)
        random.seed(seed)
        
        result = combination_monte_carlo_simulation(starting_capital, custom_metrics, num_simulations=num_simulations)
        
        # Aggregate metrics
        aggregated_results['average_profit'] += result['average_profit'] / num_seeds
        aggregated_results['hit_rate'] += result['hit_rate'] / num_seeds
        aggregated_results['total_profit'] += result['total_profit'] / num_seeds
        aggregated_results['std_dev'] += result['std_dev'] / num_seeds
        aggregated_results['sharpe_ratio'] += result['sharpe_ratio'] / num_seeds
        aggregated_results['max_drawdown'] += result['max_drawdown'] / num_seeds
        
        if not aggregated_results['cumulative_returns']:
            aggregated_results['cumulative_returns'] = [0] * len(result['cumulative_returns'])
        for i in range(len(result['cumulative_returns'])):
            aggregated_results['cumulative_returns'][i] += result['cumulative_returns'][i] / num_seeds
    
    return aggregated_results

def multi_seed_average(evs, kellys, prob_strata, odds_strata, starting_capital, max_parlay_size, num_simulations=38, num_seeds=5):
    """
    Averages the results of Monte Carlo simulations across multiple random seeds.
    """
    aggregated_results = {
        'average_ev': 0,
        'average_stake': 0,
        'average_profit': 0,
        'hit_rate': 0,
        'total_profit': 0,
        'std_dev': 0,
        'sharpe_ratio': 0,
        'max_drawdown': 0,
        'cumulative_returns': []
    }
    
    aggregated_results['average_ev'] = np.mean(np.array(evs))
    aggregated_results['average_stake'] = np.mean(np.array(kellys))

    for seed in range(num_seeds):
        np.random.seed(seed)
        random.seed(seed)
        
        result = monte_carlo_simulation(prob_strata, odds_strata, starting_capital, max_parlay_size, num_simulations)
        
        # Aggregate metrics
        aggregated_results['average_profit'] += result['average_profit'] / num_seeds
        aggregated_results['hit_rate'] += result['hit_rate'] / num_seeds
        aggregated_results['total_profit'] += result['total_profit'] / num_seeds
        aggregated_results['std_dev'] += result['std_dev'] / num_seeds
        aggregated_results['sharpe_ratio'] += result['sharpe_ratio'] / num_seeds
        aggregated_results['max_drawdown'] += result['max_drawdown'] / num_seeds
        
        if not aggregated_results['cumulative_returns']:
            aggregated_results['cumulative_returns'] = [0] * len(result['cumulative_returns'])
        for i in range(len(result['cumulative_returns'])):
            aggregated_results['cumulative_returns'][i] += result['cumulative_returns'][i] / num_seeds
    
    return aggregated_results

if __name__ == '__main__':
    starting_capital = 100  # Set initial account balance
    max_parlay_sizes = [1, 2, 3, 4]
    custom_counts = [{
        1: 1,
        2: 1,
        3: 1,
        4: 1 
    },
    {
        1: 1,
        2: 3,
        3: 1,
        4: 0 
    },
    {
        1: 3,
        2: 2,
        3: 1,
        4: 0 
    },
    {
        1: 4,
        2: 3,
        3: 0,
        4: 0 
    }]
    num_simulations = 38*2
    probabilities, odds, evs_dict, kellys_dict, custom_metrics = get_data_from_matchdays(load_matches_from_folder(), max_parlay_sizes[-1],custom_counts)
    print(custom_metrics)
    
    prob, odds = get_all_strata(probabilities, odds)
    num_seeds = 1000
    single_results = {}
    combination_results = {}

    for max_parlay_size in max_parlay_sizes:
        print(f"Running Monte Carlo for Max Parlay Size = {max_parlay_size}...")
        prob_samples, odds_samples = stratified_sampling(prob, max_parlay_size, num_simulations), stratified_sampling(odds, max_parlay_size, num_simulations)[::-1]
        combined = list(zip(prob_samples, odds_samples))

        random.shuffle(combined)

        array_1_shuffled, array_2_shuffled = zip(*combined)

        prob_samples = list(array_1_shuffled)
        odds_samples = list(array_2_shuffled)
        kellys = get_other_metrics(kellys_dict, max_parlay_size)
        evs = get_other_metrics(evs_dict, max_parlay_size)
        single_results[max_parlay_size] = multi_seed_average(evs, kellys, prob_samples, odds_samples, starting_capital, max_parlay_size, num_simulations, num_seeds)

    for idx, custom_metric in enumerate(custom_metrics):
        label = str(custom_metric['custom_parlay_count'])  # Use the custom parlay count as the label
        print(f"Running Monte Carlo for Custom Parlay Count {label}...")
        combination_results[label] = multi_seed_combination_average(custom_metric, starting_capital, num_seeds, num_simulations)
    # Combine single and combination results
    all_labels = [str(size) for size in max_parlay_sizes] + list(combination_results.keys())

    # Prepare combined data for visualization
    all_std_devs = [single_results[size]['std_dev'] for size in max_parlay_sizes] + [combination_results[label]['std_dev'] for label in combination_results.keys()]
    all_sharpe_ratios = [single_results[size]['sharpe_ratio'] for size in max_parlay_sizes] + [combination_results[label]['sharpe_ratio'] for label in combination_results.keys()]
    all_max_drawdowns = [single_results[size]['max_drawdown'] for size in max_parlay_sizes] + [combination_results[label]['max_drawdown'] for label in combination_results.keys()]
    all_hit_rates = [single_results[size]['hit_rate'] for size in max_parlay_sizes] + [combination_results[label]['hit_rate'] for label in combination_results.keys()]
    all_avg_profits = [single_results[size]['average_profit'] for size in max_parlay_sizes] + [combination_results[label]['average_profit'] for label in combination_results.keys()]

    # Bar charts for metrics
    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    fig.suptitle("Monte Carlo Metrics for Parlays and Combinations", fontsize=16, y=0.97)

    # Standard Deviation
    axes[0, 0].bar(all_labels, all_std_devs, color='blue', alpha=0.7)
    axes[0, 0].set_title("Standard Deviation", fontsize=11)
    axes[0, 0].set_xlabel("Parlay Size / Custom Parlay Count", fontsize=11)
    axes[0, 0].set_ylabel("Std", fontsize=11)
    axes[0, 0].tick_params(axis='x', rotation=45)

    # Sharpe Ratio
    axes[0, 1].bar(all_labels, all_sharpe_ratios, color='green', alpha=0.7)
    axes[0, 1].set_title("Sharpe Ratio", fontsize=11)
    axes[0, 1].set_xlabel("Parlay Size / Custom Parlay Count", fontsize=11)
    axes[0, 1].set_ylabel("Sharpe Ratio", fontsize=11)
    axes[0, 1].tick_params(axis='x', rotation=45)

    # Max Drawdown
    axes[1, 0].bar(all_labels, all_max_drawdowns, color='red', alpha=0.7)
    axes[1, 0].set_title("Max Drawdown", fontsize=11)
    axes[1, 0].set_xlabel("Parlay Size / Custom Parlay Count", fontsize=11)
    axes[1, 0].set_ylabel("Max Drawdown", fontsize=11)
    axes[1, 0].tick_params(axis='x', rotation=45)

    # Hit Rate
    axes[1, 1].bar(all_labels, all_hit_rates, color='purple', alpha=0.7)
    axes[1, 1].set_title("Hit Rate", fontsize=11)
    axes[1, 1].set_xlabel("Parlay Size / Custom Parlay Count", fontsize=11)
    axes[1, 1].set_ylabel("Hit Rate", fontsize=11)
    axes[1, 1].tick_params(axis='x', rotation=45)

    # Average Profit
    axes[2, 0].bar(all_labels, all_avg_profits, color='orange', alpha=0.7)
    axes[2, 0].set_title("Average Profits", fontsize=11)
    axes[2, 0].set_xlabel("Parlay Size / Custom Parlay Count", fontsize=11)
    axes[2, 0].set_ylabel("Average Profit", fontsize=11)
    axes[2, 0].tick_params(axis='x', rotation=45)

    plt.tight_layout(pad=2.5, h_pad=3.5, w_pad=2.0, rect=[0, 0, 1, 0.95])
    plt.show()

    # Equity Curve Plot
    plt.figure(figsize=(14, 8))
    for max_parlay_size, metrics in single_results.items():
        plt.plot(metrics['cumulative_returns'], label=f"Parlay Size {max_parlay_size}")

    for label, metrics in combination_results.items():
        plt.plot(metrics['cumulative_returns'], label=f"Custom Parlay Count {label}")

    plt.title("Equity Curve Over Simulations", fontsize=16)
    plt.xlabel("Matchweek", fontsize=14)
    plt.ylabel("Account Balance", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
