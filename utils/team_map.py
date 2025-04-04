team_name_map = {
    "QPR": "Queens Park Rangers",
    "Man Utd": "Manchester United",
    "Grimsby": "Grimsby Town",
    "Notts": "Notts County",
    "Birmingham": "Birmingham City",
    "Sheff Utd": "Sheffield United",
    "Cambridge Utd": "Cambridge United",
    "Bodø/Glimt": "Bodo",
    "Olympiakos": "Olympiacos Piraeus",
    "Athletic Club": "Athletic Bilbao",
    "Roma": "AS Roma",
    "M'gladbach": "Borussia Mönchengladbach",
    "Mainz 05": "FSV Mainz",
    "L Orient": "Leyton Orient FC",
    "Man City": "Manchester City",
    "Milan": "AC Milan",
    "Inter": "Inter Milan",
    "Armenia": "Armenië",
    "Georgia": "Georgië",
    "Turkey": "Turkije",
    "Hungary": "Hongarije",
    "Netherlands": "Nederland",
    "Spain": "Spanje",
    "Italy": "Italië",
    "Germany": "Duitsland",
    "Croatia": "Kroatië",
    "France": "Frankrijk",
    "Denmark": "Denemarken",
    "Portugal": "Portugal",
    "Ukraine": "Oekraine",
    "Belgium": "België",
    "Bulgaria": "Bulgarije",
    "Ireland": "Ierland",
    "Austria": "Oostenrijk",
    "Serbia": "Servië",
    "Greece": "Griekenland",
    "Scotland": "Schotland",
    "Kosovo": "Kosovo",
    "Iceland": "IJsland",
    "Slovakia": "Slowakije",
    "Slovenia": "Slovenie",
    "MK Dons": "Milton Keynes Dons",
    "Leganés": "Leganes",
    "Saint-Étienne": "AS Saint-Etienne",
    "Nottm Forest": "Nottingham Forest",
    
}

def get_translation(input_team: str) -> str:
    return team_name_map.get(input_team.strip(), input_team)

reverse_team_name_map = {v: k for k, v in team_name_map.items()}

def get_reverse_translation(translated_team: str) -> str:
    return reverse_team_name_map.get(translated_team.strip(), translated_team)

#print(get_translation("Slovenia"))
#print(get_reverse_translation("Slovenie"))