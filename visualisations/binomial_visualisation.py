# file: binomial_distribution_analysis.py

import numpy as np
import matplotlib.pyplot as plt

# Parameters for the Binomial Model
n_matches = 9  # Number of matches in the parlay
p_correct = 1 / 3  # Probability of predicting a match correctly
n_simulations = 10000  # Number of parlay simulations

# Simulate the number of correct predictions for each parlay
simulated_correct_predictions = np.random.binomial(n=n_matches, p=p_correct, size=n_simulations)

# Calculate probabilities for each possible number of correct predictions
outcomes = np.arange(0, n_matches + 1)
counts = np.bincount(simulated_correct_predictions, minlength=n_matches + 1)
probabilities = counts / n_simulations

# Find the most commonly occurring number of hits
most_common_hits = outcomes[np.argmax(probabilities)]
print(f"The most commonly occurring number of hits is: {most_common_hits}")

# Plot the probability distribution
plt.figure(figsize=(10, 6))
plt.bar(outcomes, probabilities, color='blue', alpha=0.7, edgecolor='black')
plt.title(f"Binomial Distribution of Correct Predictions (n={n_matches}, p={p_correct:.2f})")
plt.xlabel("Number of Correct Predictions")
plt.ylabel("Probability")
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
