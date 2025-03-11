from playwright.sync_api import sync_playwright
import json
from pathlib import Path
import time
import random as rand
import pandas as pd



SESSION_FILE = "session_cookies.json"

def save_cookies(page):
    cookies = page.context.cookies()
    with open(SESSION_FILE, "w") as f:
        json.dump(cookies, f)

def load_cookies(page):
    if Path(SESSION_FILE).exists():
        with open(SESSION_FILE, "r") as f:
            cookies = json.load(f)
        page.context.add_cookies(cookies)
        print("Loaded session cookies.")

def initialise(url):
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    load_cookies(page)

    page.goto(url, wait_until="domcontentloaded", timeout=20000)
    for i in range(5, 10):
        time.sleep(rand.uniform(1.5, 2))
    
    # check if hCaptcha is present
    if page.query_selector("iframe[src*='hcaptcha.com']"):
        print("\n🚨 Captcha detected! Solve it manually in the browser. 🚨")
        input("Press Enter after solving the captcha manually...")

        # save session cookies after captcha is solved
        save_cookies(page)
        print("\n✅ Captcha solved and session saved. Continuing...")

    return p, browser, context, page
    
def login(page, username, password):

    page.click("text=Inloggen")

    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    

    page.click("button[type='submit']")
    
    page.wait_for_load_state("domcontentloaded", timeout=20000)

    for i in range(5, 10):
        time.sleep(rand.uniform(1.5, 2))
    
    print("\n✅ Login successful.")
    


def normalize_risk(max_risk, pending_bets):
    multiplier = max_risk/sum(pending_bets["de_normalized_risk"])
    
    for idx, row in pending_bets.iterrows():
        pending_bets.loc[idx, 'normalized_risk'] = row['de_normalized_risk'] * multiplier

    return pending_bets

def initialize_placed_bets_file(today):
    placed_bets_file = f"data/placed_bets_{today}.csv"
    if not Path(placed_bets_file).exists():
        df = pd.DataFrame(columns=[
            "date", "date_placed", "league", "home_team", "away_team", 
            "home_win_%", "draw_%", "away_win_%", "odds_home", "odds_draw", 
            "odds_away", "bet", "de_normalized_risk", "normalized_risk", "ev"
        ])
        df.to_csv(placed_bets_file, index=False)
    return placed_bets_file

def record_bet(home_team, away_team, league, risk, bet, home_win, draw, away_win, odds_home, odds_draw, odds_away, de_norm_risk, date, ev, placed_bets_file):
    placed_bets = pd.DataFrame({
        "date": date,
        "date_placed": [pd.Timestamp.now()],
        "league": league,
        "home_team": home_team,
        "away_team": away_team,
        "home_win_%": home_win,
        "draw_%": draw,
        "away_win_%": away_win,
        "odds_home": odds_home,
        "odds_draw": odds_draw,
        "odds_away": odds_away,
        "bet": bet,
        "de_normalized_risk": de_norm_risk,
        "normalized_risk": risk,
        "ev": ev
    })

    placed_bets.to_csv(placed_bets_file, mode='a', header=False, index=False)


def place_bet(page, home_team, away_team, risk, bet, league, home_win, draw, away_win, odds_home, odds_draw, odds_away, de_norm_risk, date, ev, placed_bets_file):
    page.fill("[data-testid='search-field']", f"{home_team}, {away_team}")
    time.sleep(1)
    if bet == "home":
        bet_label = f"{home_team}"
    elif bet == "draw":
        bet_label = f"Gelijkspiel"
    elif bet == "away":
        bet_label = f"{away_team}"

    match_section = page.locator(f"div:has-text('{bet_label}')").locator("..")
    bet_button = match_section.locator(f"[data-testid='outcome-button']:has-text('{bet_label}')")
    bet_button.click()

    time.sleep(1)

    bet_slip = page.locator("[data-testid='leg-user-input-stake-wrapper']")
    stake_input = bet_slip.locator("input[data-testid='stake-input']")

    # Fill in the risk amount
    #risk = 0.10 # testing


    stake_input.fill(str(risk))

    time.sleep(1)

    ok_button = page.locator("button:has-text('Plaats weddenschap')")
    ok_button.click()

    time.sleep(2)

    record_bet(home_team, away_team, league, risk, bet, home_win, draw, away_win, odds_home, odds_draw, odds_away, de_norm_risk, date, ev, placed_bets_file)


def get_bet_list(pending_bets):
    bet_list = []
    for idx, row in pending_bets.iterrows():
            bet_list.append({
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "final_probability": row[f"{row["bet"]}_win_%"],
            "odds": row[f"odds_{row["bet"]}"],
            "initial_risk": row["de_normalized_risk"],
            "bet": row["bet"]
            })
    return bet_list

def place_all_pending_bets(pending_bets, username, password):
    today = pd.Timestamp.now()
    placed_bets_file = initialize_placed_bets_file(today)
    url = "https://sport.toto.nl/"
    
    p, browser, context, page = initialise(url)

    page.click("text=AKKOORD")

    login(page, f"{username}", f"{password}")

    page.mouse.click(10, 10) # get rid of pop up

    balance_element = page.query_selector(".account-menu-deposit-items")
    if balance_element:
        balance_text = balance_element.inner_text().strip().replace("€", "").replace(",", ".") 
        balance = float(balance_text)
    else:
        print("Balance not found.")
        balance = 0.0
        
    balance = 90.87

    pending_bets = normalize_risk(max_risk=balance*0.9, pending_bets=pending_bets)
    
    for idx, row in pending_bets.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]
        risk = round(row["normalized_risk"], 2)
        print(risk)
        
        bet_odds = row[f"odds_{row['bet']}"]
        bet_odds = str(bet_odds).replace(".", ",")
        bet = row["bet"]

        league = row["league"]
        home_win = row["home_win_%"]
        draw = row["draw_%"]
        away_win = row["away_win_%"]
        odds_home = row["odds_home"]
        odds_draw = row["odds_draw"]
        odds_away = row["odds_away"]
        de_norm_risk = row["de_normalized_risk"]
        date = row["date"]
        ev = row["ev"]
        i=0
        place_bet(
    page, home_team, away_team, risk, bet, 
    league, home_win, draw, away_win, 
    odds_home, odds_draw, odds_away, 
    de_norm_risk, date, ev, placed_bets_file
)

    time.sleep(30)

    browser.close()


if __name__ == "__main__":
    pending_bets = pd.read_csv("data/pending_bets.csv")
    username = "madhavv197@gmail.com"
    password = "vIjay007007!"
    place_all_pending_bets(pending_bets=pending_bets, username=username, password=password)