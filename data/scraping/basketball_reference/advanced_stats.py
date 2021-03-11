"""
Retrieves the advanced statistics of all the players in a given season via basketball-reference.com.
"""

import pandas as pd

from .bball_ref_utils import *

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_full_advanced_stats(season):
    """
    Returns a list containing the advanced stats of all of the players who played in the passed season.
        
    :param season: The season from which advanced season statistics will be returned.
    :return: A list of dictionaries holding the advanced statistics of all the players in the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"NBA_{season}_advanced.html"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find(id="advanced_stats")
    trs = table.find_all("tr", {"class":["full_table", "partial_table"]})

    return get_rows_dict(trs, store_new_player_func=store_new_player_advanced_stats, update_player_func=None)

# Functions to pass to `get_rows_dict()`:

def store_new_player_advanced_stats(tr):
    """
    Based on a passed <tr> tag, stores the essential advanced statistics stored in the tag in a player dictionary and returns the dictionary.

    :param tr: A <tr> tag containing data related to the advanced season statistics of a singular player.
    :return: A dictionary containing the advanced season statistics of the player represented by the passed <tr> tag.
    """
    player = {}

    for td in tr.find_all("td"):    # Scrapes and stores data related to the player in this row
        data_type = td.get("data-stat")
        if data_type == "player":
            player["id"] = td.get("data-append-csv")    # A unique identifier used by basketball-reference.com
        
        player[data_type] = td.get_text()

    player["multi_team_player"] = 0

    return player

def get_full_advanced_stats_df(season):
    """
    Returns a pandas DataFrame holding the advanced season statistics of all players in the passed season.

    :param season: The season from which advanced season statistics will be returned.
    :return: A pandas DataFrame holding the advanced season statistics of all the players in the passed season.
    """
    stats = get_full_advanced_stats(season)
    stats_df = pd.DataFrame.from_dict(stats)

    return stats_df
