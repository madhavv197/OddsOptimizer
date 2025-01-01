# file: capital_simulation.py

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)

starting_capital = 100  # Initial capital
stake_per_parlay = 1  # Fixed stake per parlay
probability_per_parlay =  0.0034802086868647  # Odds for hitting all 9 matches
return_per_parlay = 931 # Total return multiplier for a win

# Simulation durations
week_durations = [100,1000,10000, 100000]

# Function to simulate capital history for a given number of weeks
def simulate_capital(weeks):
    np.random.seed(0)
    capital = starting_capital
    capital_history = [capital]
    for week in range(weeks):
        if np.random.rand() < probability_per_parlay:
            capital += return_per_parlay * stake_per_parlay - stake_per_parlay  # Win
        else:
            capital -= stake_per_parlay  # Loss
        capital_history.append(capital)
    return capital_history

# Create subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 15), layout= 'constrained')
axes = axes.flatten()

for i, weeks in enumerate(week_durations):
    capital_history = simulate_capital(weeks)
    axes[i].plot(capital_history, color='green', alpha=0.8)
    axes[i].set_title(f"({weeks} weeks)")
    axes[i].set_xlabel("Weeks")
    axes[i].set_ylabel("Equity")
    axes[i].grid(True, linestyle='--', alpha=0.6)

# Remove unused subplot (if any)
if len(axes) > len(week_durations):
    fig.delaxes(axes[-1])

plt.show()
