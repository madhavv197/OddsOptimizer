from playwright.sync_api import sync_playwright
import json
from pathlib import Path
import time
import random as rand
import pandas as pd
from ev_calc import find_best_multiplier


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

def place_bet(page, home_team, away_team, risk, bet, bet_odds):
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

    # Confirm the bet by clicking the OK button
    ok_button = page.locator("button:has-text('Plaats weddenschap')")
    ok_button.click()

    time.sleep(2)


def normalize_risk(bet_list, current_balance, pending_bets):
    best_multiplier, final_total_risk = find_best_multiplier(bet_list, max_risk=0.9*current_balance, step=0.01)

    print(f"Best multiplier found: {best_multiplier} with total risk: {final_total_risk}")

    for idx, row in pending_bets.iterrows():
        if row["bet"] is not None:
            pending_bets.loc[idx, 'normalized_risk'] = row['de_normalized_risk'] * best_multiplier

    return pending_bets

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

    url = "https://sport.toto.nl/"
    
    p, browser, context, page = initialise(url)

    page.click("text=AKKOORD")

    login(page, f"{username}", f"{password}")

    page.mouse.click(10, 10) # get rid of pop up

    balance_element = page.query_selector(".account-menu-deposit-items")
    if balance_element:
        balance_text = balance_element.inner_text().strip().replace("€", "").replace(",", ".")  # Convert to standard float format
        try:
            balance = float(balance_text)
        except ValueError:
            print("Error: Unable to parse balance from:", balance_text)
            balance = 0.0  # Fallback value
    else:
        print("Balance not found.")
        balance = 0.0  # Default value in case balance is not found

    bet_list = get_bet_list(pending_bets=pending_bets)

    pending_bets = normalize_risk(bet_list=bet_list, current_balance=balance, pending_bets=pending_bets)

    for idx, row in pending_bets.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]
        risk = row["normalized_risk"]
        bet_odds = row[f"odds_{row["bet"]}"]
        bet_odds = str(bet_odds).replace(".", ",")
        bet = row["bet"]
        print(bet_odds)
        place_bet(page, home_team, away_team, risk, bet, bet_odds)

    time.sleep(30)

    browser.close()


if __name__ == "__main__":
    pending_bets = pd.read_csv("data/pending_bets.csv")
    username = "madhavv197@gmail.com"
    password = "vIjay007007!"
    place_all_pending_bets(pending_bets=pending_bets, username=username, password=password)