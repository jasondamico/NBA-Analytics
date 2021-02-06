"""
Retrieves the team a group of players played on in a specified season according to basketball-reference.com
"""

from bball_ref_utils import *

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_player_team_map(season):
    """
    Given a passed season, returns a map of player names and the team they played for in that season.

    :param season: The season from which a map of team records will be returned.
    :return: A map linking team names to the record they had in the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"NBA_{season}_totals.html"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find(id="totals_stats")
    trs = table.find_all("tr", {"class":["full_table", "partial_table"]})

    player_team_map = {}
    most_played_team = None
    multiple_team_player = None

    for tr in trs:
        team = tr.find_all("td", {"data-stat":"team_id"})[0].get_text()
        name = tr.find_all("td", {"data-stat":"player"})[0].get_text()

        # Handling of players who played for multiple teams in the passed season.
        # NOTE: If a player played for more than one team in the passed season, the team he played the most amount of games for is used in the map.        
        if isinstance(most_played_team, dict):    # i.e., if there is still a player who hasn't been added to the map
            games_played = int(tr.find_all("td", {"data-stat": "g"})[0].get_text())

            if name == multiple_team_player:    # i.e., the player in this loop is the same one that is being handled due to playing for multiple teams
                if games_played > most_played_team["games_played"]:
                    most_played_team["team"] = team
                    most_played_team["games_played"] = games_played
            else:
                player_team_map[multiple_team_player] = most_played_team["team"]
                most_played_team = None
                multiple_team_player = None
        
        # Initializes multiple team handling sequence
        if team == "TOT":
            multiple_team_player = name
            most_played_team = {
                "team": None,
                "games_played": 0
            }
        elif not most_played_team:
            player_team_map[name] = team

    if most_played_team:
        player_team_map[multiple_team_player] = most_played_team["team"]

    return player_team_map
