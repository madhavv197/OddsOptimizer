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

if __name__ == '__main__':
    ev = calculate_parlay_ev(parlay)