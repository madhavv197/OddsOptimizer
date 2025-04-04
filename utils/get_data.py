from datetime import datetime
from bs4 import BeautifulSoup
import time
import random as rand
from playwright.sync_api import sync_playwright
import json
from pathlib import Path
import re
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.team_map import get_translation, get_reverse_translation


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

def initialise(url, div_class="_match-card_1u4oy_1", odds=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        load_cookies(page)

        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        for i in range(5, 10):
            time.sleep(rand.uniform(1.5, 2))
        

        # Check if hCaptcha is present
        if page.query_selector("iframe[src*='hcaptcha.com']"):
            print("\n🚨 Captcha detected! Solve it manually in the browser. 🚨")
            input("Press Enter after solving the captcha manually...")

            # Save session cookies after captcha is solved
            save_cookies(page)
            print("\n✅ Captcha solved and session saved. Continuing...")
        

        soup = BeautifulSoup(page.content(), "html.parser")
        
        with open("page_loaded.txt", "w") as f:
            f.write(soup.prettify())

        match_cards = soup.find_all("div", class_=div_class)

        return soup, match_cards

def get_future_matches():
    now = datetime.now()
    soup, match_cards = initialise("https://dataviz.theanalyst.com/opta-football-predictions/")
    future_matches = []
    live_check = 0
    for match in match_cards:
        meta = match.find("div", class_="_match-card-meta_1u4oy_18")
        if not meta:
            continue

        league_div = meta.find("div", class_="_match-card-right-label_1u4oy_83")
        league_name = league_div.text.strip() if league_div else "Unknown"

        date_time_divs = meta.find_all("div", class_="_match-card-right-label_1u4oy_83")
        if len(date_time_divs) < 2:
            continue

        match_date_str = date_time_divs[1].text.strip()

        current_year = datetime.now().year

        match_date_str = f"{current_year} {match_date_str}" 

        try:
            if "LIVE" in match_date_str:
                if live_check == 0:
                    print(f"Skipping live matches: {match_date_str}")
                    live_check = 1
            else:
                match_date = datetime.strptime(match_date_str, "%Y %b %d @ %H:%M")
        except ValueError:
            print(f"Could not parse date: {match_date_str}")
            continue

        if match_date < now:
            continue

        tbody = match.find("tbody")
        if not tbody:
            continue

        rows = tbody.find_all("tr")
        if len(rows) < 2:
            continue

        # Extract Home Team
        home_team_span = rows[0].find("span")
        home_team = home_team_span.text.strip() if home_team_span else "Unknown"

        tds_home = rows[0].find_all("td", recursive=False)

        # Check if PR exists (Nations League doesn't have PR, other leagues do)
        if len(tds_home) == 3:  # No PR case (e.g., Nations League)
            home_win_prob = tds_home[1].text.strip()
            draw_td = tds_home[2]
        else:  # PR exists (e.g., Let and Leo)
            home_pr = tds_home[1].text.strip()
            try:
                home_win_prob = tds_home[2].text.strip()
            except:
                home_win_prob = "0%"
            try:
                draw_td = tds_home[3]
            except:
                draw_td = None

        # Extract Draw Probability
        if draw_td:
            draw_divs = draw_td.find_all("div")
            draw_prob = draw_divs[2].text.strip() if len(draw_divs) > 1 else "Unknown"
        else:
            draw_prob = "0%"

        # Extract Away Team
        away_team_span = rows[1].find("span")
        away_team = away_team_span.text.strip() if away_team_span else "Unknown"

        tds_away = rows[1].find_all("td", recursive=False)

        if len(tds_away) == 2:  # No PR case
            away_win_prob = tds_away[1].text.strip()
        else:  # PR exists
            away_pr = tds_away[1].text.strip()
            away_win_prob = tds_away[2].text.strip()

        # Print results for debugging
        #print(f"Home Team: {home_team}, Home PR: {home_pr if 'home_pr' in locals() else 'N/A'}, Home Win Prob: {home_win_prob}")
        #print(f"Away Team: {away_team}, Away PR: {away_pr if 'away_pr' in locals() else 'N/A'}, Away Win Prob: {away_win_prob}")
        #print(f"Draw Probability: {draw_prob}")

        match_data = {
            "league": league_name,
            "date": match_date.strftime('%d/%m/%Y %H:%M'),
            "home_team": home_team,
            "home_pr": home_pr if "home_pr" in locals() else 0,
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_team": away_team,
            "away_pr": away_pr if 'away_pr' in locals() else 0,
            "away_win_prob": away_win_prob,
        }
        future_matches.append(match_data)
    
    #print(future_matches)

    return future_matches

def get_past_matches():
    now = datetime.now()
    soup, match_cards = initialise("https://dataviz.theanalyst.com/opta-football-predictions/")
    future_matches = []
    past_matches = []
    live_check = 0
    for match in match_cards:
        meta = match.find("div", class_="_match-card-meta_1u4oy_18")
        if not meta:
            continue

        league_div = meta.find("div", class_="_match-card-right-label_1u4oy_83")
        print(league_div)
        league_name = league_div.text.strip() if league_div else "Unknown"

        # Extract match date
        date_time_divs = meta.find_all("div", class_="_match-card-right-label_1u4oy_83")
        if len(date_time_divs) < 2:
            continue

        match_date_str = date_time_divs[1].text.strip()
        current_year = datetime.now().year
        match_date_str = f"{current_year} {match_date_str}"

        try:
            if "LIVE" in match_date_str:
                if live_check == 0:
                    print(f"Skipping live matches: {match_date_str}")
                    live_check = 1 
            else:
                match_date = datetime.strptime(match_date_str, "%Y %b %d @ %H:%M")
        except ValueError:
            print(f"Could not parse date: {match_date_str}")
            continue

        # Skip future matches
        if match_date > now:
            continue

        tbody = match.find("tbody")
        if not tbody:
            continue
        rows = tbody.find_all("tr")
        if len(rows) < 2:
            continue

        tds_home = rows[0].find_all("td")
        home_team = tds_home[0].text.strip() if len(tds_home) > 0 else "Unknown"
        home_goals = tds_home[1].text.strip() if len(tds_home) > 1 else "Unknown"

        tds_away = rows[1].find_all("td")
        away_team = tds_away[0].text.strip() if len(tds_away) > 0 else "Unknown"
        away_goals = tds_away[1].text.strip() if len(tds_away) > 1 else "Unknown"

        outcome = "draw" if home_goals == away_goals else "home" if home_goals > away_goals else "away"

        match_data = {
            "league": league_name,
            "date": match_date.strftime('%d/%m/%Y %H:%M'),
            "home_team": home_team,
            "home_goals": home_goals,
            "away_team": away_team,
            "away_goals": away_goals,
            "outcome": outcome,
        }
        past_matches.append(match_data)
    print(past_matches)
    return past_matches

def get_odds():
    league_urls = {
        "epl": "https://sport.toto.nl/wedden/sport/567/engeland-premier-league/wedstrijden",
        "leo": "https://sport.toto.nl/wedden/sport/578/engeland-league-1/wedstrijden",
        "let": "https://sport.toto.nl/wedden/sport/688/engeland-league-2/wedstrijden",
        "cha": "https://sport.toto.nl/wedden/sport/691/engeland-championship/wedstrijden",
        "sea": "https://sport.toto.nl/wedden/sport/644/italie-serie-a/wedstrijden",
        "ucl": "https://sport.toto.nl/wedden/sport/569/uefa-champions-league/wedstrijden",
        "uel": "https://sport.toto.nl/wedden/sport/3218/uefa-europa-league/wedstrijden",
        "ll": "https://sport.toto.nl/wedden/sport/570/spanje-laliga/wedstrijden",
        "li1": "https://sport.toto.nl/wedden/sport/911/frankrijk-ligue-1/wedstrijden",
        "bun": "https://sport.toto.nl/wedden/sport/577/duitsland-bundesliga/wedstrijden",
        "nat": "https://sport.toto.nl/wedden/sport/9641/uefa-nations-league/wedstrijden"
    }

    #league_urls = {"ucl": "https://sport.toto.nl/wedden/sport/569/uefa-champions-league/wedstrijden"} # testing

    league_data = {}
    extracted_matches = []

    for prefix, url in league_urls.items():
        print("\n🔍 Fetching odds for", prefix.upper())

        soup, match_cards = initialise(url, div_class="selectionPrice-0-3-836", odds=True)
        matches = soup.find_all("div", class_=re.compile(r"eventListItemContent-0-3-\d+"))

        for match in matches:

            team_name_a = match.find("div", class_=re.compile(r"eventCardTeamName-0-3-\d+ eventCardTeamNameGroupedEventList-0-3-\d+"), 
                                     attrs={"data-testid": "event-card-team-name-a"})
            home_team = team_name_a.text.strip() if team_name_a else "Unknown"

            team_name_b = match.find("div", class_=re.compile(r"eventCardTeamName-0-3-\d+ eventCardTeamNameGroupedEventList-0-3-\d+"), 
                                     attrs={"data-testid": "event-card-team-name-b"})
            away_team = team_name_b.text.strip() if team_name_b else "Unknown"

            odds = match.find_all("span", class_=re.compile(r"outcomePriceCommon-0-3-\d+"))
            win_odds = odds[0].text.strip() if len(odds) > 0 else "0"
            draw_odds = odds[1].text.strip() if len(odds) > 1 else "0"
            loss_odds = odds[2].text.strip() if len(odds) > 2 else "0"

            date_div = match.find("div", class_="timeBandGroupHeader-0-3-622")
            match_date = date_div.text.strip() if date_div else "Unknown"

            match_data = {
                "league": prefix,
                "date": match_date,
                "home_team": home_team,
                "away_team": away_team,
                "win_odds": win_odds,
                "draw_odds": draw_odds,
                "loss_odds": loss_odds
            }
            extracted_matches.append(match_data)

        #print(extracted_matches)

        league_data[prefix] = extracted_matches
    #print(extracted_matches)
    return extracted_matches

#get_future_matches()
# get_past_matches()