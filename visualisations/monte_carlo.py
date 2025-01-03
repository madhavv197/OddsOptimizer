import random
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.loader import load_matches_from_folder
from src.ev_calc import test_all_parlays
from utils.get_strata import get_all_strata, stratified_sampling, get_data_from_matchdays, get_other_metrics

random.seed(0)

def simulate_matchday(odds, prob):
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
    aggregated_results['average_profit'] = np.mean(np.array(kellys))

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
    max_parlay_sizes = [1, 2, 3, 4, 5, 6, 7, 8 ,9, 10]
    num_simulations = 38*2
    probabilities, odds, evs_dict, kellys_dict = get_data_from_matchdays(load_matches_from_folder())

    
    prob, odds = get_all_strata(probabilities, odds)
    num_seeds = 1000

    results = {}

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
        results[max_parlay_size] = multi_seed_average(evs, kellys, prob_samples, odds_samples, starting_capital, max_parlay_size, num_simulations, num_seeds)

    # Bar charts for metrics
    fig, axes = plt.subplots(3, 2, figsize=(14, 18))  # Increased figsize for more space
    fig.suptitle("Monte Carlo Metrics by Parlay Size", fontsize=16, y=0.97)  # Adjust title position and size

    # Prepare data
    std_devs = [results[size]['std_dev'] for size in max_parlay_sizes]
    sharpe_ratios = [results[size]['sharpe_ratio'] for size in max_parlay_sizes]
    max_drawdowns = [results[size]['max_drawdown'] for size in max_parlay_sizes]
    hit_rates = [results[size]['hit_rate'] for size in max_parlay_sizes]
    evs_data = [np.mean(evs_dict[size]) for size in max_parlay_sizes]
    kellys_data = [np.mean(kellys_dict[size]) for size in max_parlay_sizes]

    # Plot standard deviation
    axes[0, 0].bar(max_parlay_sizes, std_devs, color='blue', alpha=0.7)
    axes[0, 0].set_title("Standard Deviation", fontsize=11)
    axes[0, 0].set_xlabel("Parlay Size", fontsize=11)
    axes[0, 0].set_ylabel("Std", fontsize=11)

    # Plot Sharpe ratio
    axes[0, 1].bar(max_parlay_sizes, sharpe_ratios, color='green', alpha=0.7)
    axes[0, 1].set_title("Sharpe Ratio", fontsize=11)
    axes[0, 1].set_xlabel("Parlay Size", fontsize=11)
    axes[0, 1].set_ylabel("Sharpe Ratio", fontsize=11)

    # Plot max drawdown
    axes[1, 0].bar(max_parlay_sizes, max_drawdowns, color='red', alpha=0.7)
    axes[1, 0].set_title("Max Drawdown", fontsize=11)
    axes[1, 0].set_xlabel("Parlay Size", fontsize=11)
    axes[1, 0].set_ylabel("Max Drawdown", fontsize=11)

    # Plot hit rate
    axes[1, 1].bar(max_parlay_sizes, hit_rates, color='purple', alpha=0.7)
    axes[1, 1].set_title("Hit Rate", fontsize=11)
    axes[1, 1].set_xlabel("Parlay Size", fontsize=11)
    axes[1, 1].set_ylabel("Hit Rate", fontsize=11)

    # Plot EVs
    axes[2, 0].bar(max_parlay_sizes, evs_data, color='orange', alpha=0.7)
    axes[2, 0].set_title("Expected Values (EVs)", fontsize=11)
    axes[2, 0].set_xlabel("Parlay Size", fontsize=11)
    axes[2, 0].set_ylabel("EVs", fontsize=11)

    # Plot Kellys
    axes[2, 1].bar(max_parlay_sizes, kellys_data, color='cyan', alpha=0.7)
    axes[2, 1].set_title("Kelly Criterion Stakes", fontsize=11)
    axes[2, 1].set_xlabel("Parlay Size", fontsize=11)
    axes[2, 1].set_ylabel("Kellys", fontsize=11)

    # Apply tight layout and manually adjust spacing
    plt.tight_layout(pad=2.5, h_pad=3.5, w_pad=2.0, rect=[0, 0, 1, 0.95])  # Add more padding and space
    plt.show()

    # Equity curve plot
    plt.figure(figsize=(14, 8))  # Increased size for better readability
    for max_parlay_size, metrics in results.items():
        plt.plot(metrics['cumulative_returns'], label=f"Parlay Size {max_parlay_size}")

    plt.title("Equity Curve Over Simulations", fontsize=16)
    plt.xlabel("Matchweek", fontsize=14)
    plt.ylabel("Account Balance", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
