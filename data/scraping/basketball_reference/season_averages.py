"""
Retrieves the team a group of players played on in a specified season according to basketball-reference.com
"""

import pandas as pd

from .bball_ref_utils import *

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_full_season_stats(season):
    """
    Returns a list containing the season averages of all of the players who played in the passed season.
        
    :param season: The season from which season averages will be returned.
    :return: A list of dictionaries holding the season average statistics of all the players in the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"NBA_{season}_per_game.html"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find(id="per_game_stats")
    trs = table.find_all("tr", {"class":["full_table", "partial_table"]})

    return get_rows_dict(trs, store_new_player_season_averages, update_player_season_averages)

def get_full_season_stats_df(season):
    """
    Returns a pandas DataFrame holding the season average statistics of all players in the passed season.

    :param season: The season from which season averages will be returned.
    :return: A pandas DataFrame holding the season average statistics of all the players in the passed season.
    """
    stats = get_full_season_stats(season)
    stats_df = pd.DataFrame.from_dict(stats)

    return stats_df

# Functions to pass to `get_rows_dict()`:

def store_new_player_season_averages(tr):
    """
    Based on a passed <tr> tag, stores the essential season average statistics stored in the tag in a player dictionary and returns the dictionary.

    :param tr: A <tr> tag containing data related to the season average staticstics of a singular player.
    :return: A dictionary containing the season average statistics of the player represented by the passed <tr> tag.
    """
    player = {}

    for td in tr.find_all("td"):    # Scrapes and stores data related to the player in this row
        data_type = td.get("data-stat")
        if data_type == "player":
            player["id"] = td.get("data-append-csv")    # A unique identifier used by basketball-reference.com
        
        player[data_type] = td.get_text()

    player["multi_team_player"] = 0

    return player

def update_player_season_averages(tr, player):
    """
    Handles the updating of season average statistics of the passed player given another passed <tr> tag that represents the same player as the one passed as a dictionary.

    :param tr: A <tr> tag containing data related to the season average staticstics of a singular player (the same player represented by the player parameter).
    :param player: A dictionary representing the season average statictics of a player that has played on multiple teams in one season.
    :return: A dictionary containing the updated season average statistics of the player represented by the passed <tr> tag and dictionary.
    """
    stored_team_games = int(player["g"])
    current_row_games_played = int(tr.find_all("td", {"data-stat":"g"})[0].get_text())

    if player["team_id"] == "TOT" or current_row_games_played > stored_team_games:      # NOTE: The statistics of the player stored are their total season stats, but the team stored is the team they played the most games for
        current_row_team = tr.find_all("td", {"data-stat":"team_id"})[0].get_text()
        player["g"] = current_row_games_played
        player["team_id"] = current_row_team

    return player
