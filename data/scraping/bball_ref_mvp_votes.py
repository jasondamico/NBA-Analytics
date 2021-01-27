"""
Performs web scraping of basketball-reference.com to obtain MVP voting stats.
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.basketball-reference.com/awards/"
RELEVANT_COL_NAMES = ["player", "votes_first", "points_won", "points_max", "award_share"]

def get_mvp_voting_map(season):
    """
    Returns a list of maps of all the players that received MVP votes for the passed season. NOTE: Season 2000 is the 1999-2000 season for basketball-reference, whereas season 2000 is 2000-2001 for balldontlie.

    :param season: The season from which a list of player voting maps will be returned.
    :return: A list of voting maps, where each element in the list is a map of how a given player received votes for the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"awards_{season}.html#mvp"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')

    mvp_table = soup.find(id='mvp')
    tds = mvp_table.find_all('td')

    players_list = get_players_list(tds)

    players_map = []

    for player in players_list:
        val_map = dict()

        for value in player:
            data_stat_val = value.get("data-stat")
            val_map[data_stat_val] = value.get_text()

        players_map.append(val_map)

    return players_map

def convert_bdl_season_to_bball_ref(season):
    """
    Considering that a year corresponding to a season means different things to the balldontlie and the basketball-reference website, returns the passed season integer to the integer that would access the same season on basketball-reference.com as is being used in the balldontlie API.

    :param season: An integer used to retrieve an NBA season from the balldontlie API.
    :return: The integer used to receive the same NBA season from the basketball-reference website as the one that was retrieved from the balldontlie API.
    """
    return season + 1

def get_players_list(tds):
    """
    Parses through the passed td tags and returns a list where each element contains a collection of td tags related to the MVP voting stats of a player.

    :param tds: A ResultSet object containing td tags from the MVP voting table.
    :return: A list of td tag collections, where each element in the list represents a player in the MVP voting table.
    """
    players_list = []
    player = []

    for td in tds:
        if td.get("csk") and player != []:
            players_list.append(player)
            player = []
        
        if is_relevant_voting_col(td.get("data-stat")):
            player.append(td)

    return players_list

def is_relevant_voting_col(col_name):
    """
    Returns a boolean corresponding to whether the passed column name is a relevant voting column (meaning that it is of use for collecting data) or not.

    :col_name: The name of the column being considered for relevance.
    :return: TRUE if the passed column name corresponds to data that is relevant for collection, FALSE otherwise.
    """
    return col_name in RELEVANT_COL_NAMES

def check_status_code(response, season):
    """
    Checks to see if the response returned a valid status code, raising an error if not.

    :param response: The response returned from a get request.
    :param season: The season being retrieved through the response.
    """
    if response.status_code in range (400, 499):
        if response.status_code == 404:
            raise Exception("404 Error: Page not found. Please check to see if there is MVP voting available for the %d season." % (season))
        else:
            exception_message = "%d Error: %s" % (response.status_code, response.reason)
            raise Exception(exception_message)
