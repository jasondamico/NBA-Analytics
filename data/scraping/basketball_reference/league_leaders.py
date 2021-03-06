"""
Retrieves league leader data for a given season from basketball-reference.com
"""

import pandas as pd

from .bball_ref_utils import *

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_full_league_leaders(season, fields):
    """
    Returns a list containing information about the league leaders for the passed fields in the specified season.
        
    :param season: The season from which league leaders statistics will be returned.
    :param fields: A list of strings containing the fields from which league leaders should be retrieved (e.g., "pts_per_g").
    :return: A list holding the league leaders of all the passed fields in the specified season.
    """
    season = convert_bdl_season_to_bball_ref(season)
    soup = get_season_leaders_soup_page(season)
    
    league_leaders = []

    for field in fields:
        field_leader = get_league_leader_from_soup_page(soup, field)
        league_leaders.append(field_leader)

    return league_leaders

def get_season_leaders_soup_page(season):
    """
    Given a passed season, returns a BeautifulSoup object holding the page used for retrieving league leaders.

    :param season: The season from which league leaders statistics will be returned.
    :return: A BeautifulSoup object of the league leaders page for the passed season.
    """
    url = BASE_URL + f"NBA_{season}_leaders.html"

    page = requests.get(url)

    check_status_code(page, season)

    return BeautifulSoup(page.content, 'html.parser')

def get_league_leader(season, field):
    """
    Given a passed season and field, returns the information about the first place player in that field in a dictionary.

    :param season: The season from which league leaders statistics will be returned.
    :param field: The field from which the league leader will be returned. 
    :return: A dictionary containing the id of the player leading the league in the given category, the name of the category they are leading the league in, and the value of their league-leading statistic.
    """
    season = convert_bdl_season_to_bball_ref(season)
    soup = get_season_leaders_soup_page(season)

    return get_league_leader_from_soup_page(soup, field)

def get_league_leader_from_soup_page(soup_page, field):
    """
    Given a passed field and BeautifulSoup object of the league leaders page, returns the information about the first place player in that field in a dictionary.

    :param soup_page: A BeautifulSoup object of the league leaders page.
    :param field: The field from which the league leader will be returned. 
    :return: A dictionary containing the id of the player leading the league in the given category, the name of the category they are leading the league in, and the value of their league-leading statistic.
    """
    leaders_div = soup_page.find(id=f"leaders_{field}")     # The div containing the information of the league leaders of a certain field.

    try:
        field_name = leaders_div.get("id")
    except:
        raise FieldNotFound(f"League leader for field {field} not found.")
    index = field_name.index("leaders_") + len("leaders_")
    field_name = field_name[index:]

    table = leaders_div.find("table", "columns")    # this table contains the 20 leaders in the given field
    first_place_tr = table.find("tr", "first_place")

    league_leader = {
        "player_id": get_player_id_from_url(first_place_tr.find("td", "who").find("a").get("href")),
        "field": field_name,
        "value": float(first_place_tr.find("td", "value").get_text())
    }

    return league_leader

def get_full_league_leaders_df(season, fields):
    """
    Returns a DataFrame object containing information about the league leaders for the passed fields in the specified season.
        
    :param season: The season from which league leaders statistics will be returned.
    :param fields: A list of strings containing the fields from which league leaders should be retrieved (e.g., "pts_per_g").
    :return: A DataFrame object holding the league leaders of all the passed fields in the specified season.
    """
    league_leaders_list = get_full_league_leaders(season, fields)
    
    return pd.DataFrame.from_dict(league_leaders_list)

class FieldNotFound(Exception):
    pass
