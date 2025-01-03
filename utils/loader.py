import ast
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.kelly import kelly_criterion

def load_matches_from_file(file_path):
    matches = []
    with open(file_path, 'r') as file:
        content = file.read()
        entries = content.split('},')
        for entry in entries:
            if not entry.strip().endswith('}'):
                entry += '}'
            match = ast.literal_eval(entry.strip())
            matches.append(match)
    return matches

def generate_outcomes(match):
    return [
        {'fixture': match['fixture'], 'outcome': 'Win', 'probability': match['win_probability'], 'odds': match['win_odds']},
        {'fixture': match['fixture'], 'outcome': 'Draw', 'probability': match['draw_probability'], 'odds': match['draw_odds']},
        {'fixture': match['fixture'], 'outcome': 'Loss', 'probability': match['loss_probability'], 'odds': match['loss_odds']}
    ]

def load_matches_from_folder():
    matchdays = os.listdir('data/season2425')
    matchday_data = []
    for matchday in matchdays:
        matchday_data.append(load_matches_from_file(os.path.join('data/season2425', matchday)))
    return matchday_data


if __name__ == '__main__':
    matches = load_matches_from_file("data/season2425/matchday21.txt")



