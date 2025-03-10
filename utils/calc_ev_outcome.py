def calculate_ev(prob, odds):
    """
    Given a probability (prob) and decimal odds,
    returns the expected value of a single 1-unit stake.
    """
    return prob * (odds - 1) - (1 - prob)