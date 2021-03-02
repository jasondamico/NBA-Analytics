"""
Retrieves the team a group of players played on in a specified season according to basketball-reference.com
"""

from unidecode import unidecode
from bball_ref_utils import *
from team_abbreviation_dict import team_abbreviation_dict

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
    multiple_team_player_id = None

    for tr in trs:
        team = tr.find_all("td", {"data-stat":"team_id"})[0].get_text()
        player_id = tr.find_all("th", {"data-stat":"ranker"})[0].get_text()
        full_name = unidecode(tr.find_all("td", {"data-stat":"player"})[0].get_text()).replace(".", "")

        # Handling of players who played for multiple teams in the passed season.
        # NOTE: If a player played for more than one team in the passed season, the team he played the most amount of games for is used in the map.        
        if multiple_team_player:    # i.e., if there is still a player who hasn't been added to the map
            games_played = int(tr.find_all("td", {"data-stat": "g"})[0].get_text())

            if player_id == multiple_team_player_id:    # i.e., the player in this loop is the same one that is being handled due to playing for multiple teams
                if games_played > most_played_team["games_played"]:
                    most_played_team["team"] = team_abbreviation_dict[team]
                    most_played_team["games_played"] = games_played
            else:   # stores multi-team player, as the player belonging to this loop of the trs is no longer the multi-team player
                player_team_map[multiple_team_player_id] = {
                    "team": most_played_team["team"],
                    "full_name": multiple_team_player["full_name"],
                }

                most_played_team = None
                multiple_team_player = None
                multiple_team_player_id = None
        
        if team == "TOT":   # Initializes multiple team handling sequence
            multiple_team_player_id = player_id
            multiple_team_player = {"full_name": full_name}
            most_played_team = {
                "team": None,
                "games_played": 0
            }
        elif not most_played_team:   # i.e., this loop contains a player that only played for a singular team
            player_team_map[player_id] = {
                "team": team_abbreviation_dict[team],
                "full_name": full_name
            }

    if most_played_team:    # checks to see if the final player in the table was one who played for multiple teams
        player_team_map[multiple_team_player_id] = {
            "team": most_played_team["team"],
            "full_name": full_name
        }

    return player_team_map
