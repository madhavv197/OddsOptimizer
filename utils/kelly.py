def kelly_criterion(probability, odds, multiplier):
    return multiplier*((probability*odds-(1-probability))/odds)

if __name__ == '__main__':
    p,b = 0.5,3
    print(f'kelly: {kelly_criterion(p,b)}')