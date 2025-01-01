import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)

starting_capital = 100
kelly_formula = lambda r, p, fraction: fraction * (r * p - (1 - p)) / r

week_durations = [10, 25, 50, 100]

def simulate_capital(weeks, kelly_fraction):
    np.random.seed(0)
    capital = starting_capital
    capital_history = [capital]

    for week in range(weeks):
        probability_per_parlay = np.random.uniform(0.3, 0.4)
        return_per_parlay = np.random.uniform(3, 5)
        current_kelly = kelly_formula(return_per_parlay, probability_per_parlay, kelly_fraction)
        stake_per_parlay = capital * current_kelly

        if np.random.rand() < probability_per_parlay:
            capital += return_per_parlay * stake_per_parlay - stake_per_parlay  # Win
        else:
            capital -= stake_per_parlay  # Loss
        capital_history.append(capital)

    return capital_history

def calculate_time_to_profitability(weeks, kelly_fractions, plot_graph=True):
    results = {}

    for fraction in kelly_fractions:
        capital_history = simulate_capital(weeks, fraction)
        time_to_profit = next((i for i, cap in enumerate(capital_history) if cap > starting_capital), -1)
        results[fraction] = time_to_profit

    if plot_graph:
        plt.figure(figsize=(10, 6))
        fractions = list(results.keys())
        times = list(results.values())
        plt.plot(fractions, times, marker='o', color='blue', label='Time to Profitability')
        plt.title(f"Time to Profitability vs Kelly Fraction ({weeks} Weeks)")
        plt.xlabel("Kelly Fraction")
        plt.ylabel("Weeks to Profitability")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(np.arange(0, 1.05, 0.05))
        plt.legend()
        plt.show()

    return results

def plot_equity_curve_for_kelly(kelly_fraction):
    fig, axes = plt.subplots(2, 2, figsize=(15, 15), layout='constrained')
    axes = axes.flatten()

    for i, weeks in enumerate(week_durations):
        capital_history = simulate_capital(weeks, kelly_fraction)
        axes[i].plot(capital_history, label=f"{weeks} weeks", color='green', alpha=0.8)
        axes[i].set_title(f"Equity Curve ({weeks} Weeks)")
        axes[i].set_xlabel("Weeks")
        axes[i].set_ylabel("Equity")
        axes[i].grid(True, linestyle='--', alpha=0.6)
        axes[i].legend()

    if len(axes) > len(week_durations):
        fig.delaxes(axes[-1])

    fig.suptitle(f"Equity Curves for Kelly Fraction: {kelly_fraction:.2f}", fontsize=16)
    plt.show()

kelly_fractions = np.arange(0.05, 1.05, 0.05)
weeks = 100

results = calculate_time_to_profitability(weeks, kelly_fractions, plot_graph=False)

specific_kelly_fraction = 0.15
plot_equity_curve_for_kelly(specific_kelly_fraction)

for fraction, time in results.items():
    print(f"Kelly Fraction: {fraction:.2f}, Time to Profitability: {time} weeks")

