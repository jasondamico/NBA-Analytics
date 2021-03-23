"""
Retrieves league leader data for a given season from basketball-reference.com
"""

import pandas as pd

from .bball_ref_utils import *

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_full_league_leaders(season, fields):
    """
    Returns a list containing information about the league leaders for the passed season.
        
    :param season: The season from which league leaders statistics will be returned.
    :param fields: A list of strings containing the fields from which league leaders should be retrieved (e.g., "pts_per_g").
    :return: A list of dictionaries holding the league leaders of all the players in the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"NBA_{season}_leaders.html"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')
