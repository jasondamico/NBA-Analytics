"""
Miscellaneous utility methods that assist in basketball-reference.com web scraping.
"""

import requests
from bs4 import BeautifulSoup

def convert_bdl_season_to_bball_ref(season):
    """
    Considering that a year corresponding to a season means different things to the balldontlie and the basketball-reference website, returns the passed season integer to the integer that would access the same season on basketball-reference.com as is being used in the balldontlie API.

    :param season: An integer used to retrieve an NBA season from the balldontlie API.
    :return: The integer used to receive the same NBA season from the basketball-reference website as the one that was retrieved from the balldontlie API.
    """
    return season + 1

def get_rows_dict(trs, store_new_player_func=None, update_player_func=None):
    """
    Returns a list of dictionaries, where each dictionary holds the data passed from a row in the passed list of <tr> tags.

    :param trs: A list of <tr> tags.
    :param store_new_player_func: A function that returns a dictionary stored given a <tr> tag passed to it. The client must pass a function that parses through and stores data in a dictionary to their liking.
    :param update_player_func: A function that returns an updated dictionary in the event of a multi-team player. This function takes an argument of a <tr> tag representing a player that has been deemed as a multi-team player, with another argument containing the dictionary that currently represents the repeat player. The client should implement a function that updates and returns the passed dictionary to their liking given the data stored in the incoming <tr> tag. May be omitted if there is no purpose in updating the stored player when a new row is encountered.
    :return: A list of dictionaries containing the data held by each passed <tr> tag.
    """
    players = []
    player = {}

    for i in range(len(trs) + 1):
        try:
            tr = trs[i]
        except:
            players.append(player)  # Appends the final player, but exits loop and does not scrape as the table is complete
            continue

        player_id = tr.find_all("td", {"data-stat":"player"})[0].get("data-append-csv")

        if bool(player) and player_id != player["id"]:   # i.e., if this isn't the first loop or the player id from this row is different than the previous row
            players.append(player)  # This row is a different player than the previous row, meaning that the previous row may be stored        

        if not bool(player) or player_id != player["id"]:
            player = store_new_player_func(tr)
        else:   # Initializes multiple team handling sequence
            player["multi_team_player"] = 1

            if update_player_func:
                player = update_player_func(tr, player)

    return players

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

def get_player_id_from_url(url):
    """
    Retrieves and returns the player id from the URL to the player's profile page.

    :param url: A URL linking to the profile page of a player (e.g., https://www.basketball-reference.com/players/b/bealbr01.html).
    :return: The id of the player who is represented on the profile page linked.
    """
    # player id held between the last forward slash and the extention
    left_index = url.rfind("/") + 1
    right_index = url.index(".html")

    return url[left_index: right_index]
