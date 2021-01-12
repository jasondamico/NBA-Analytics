"""
Performs web scraping of basketball-reference.com to obtain MVP voting stats.
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.basketball-reference.com/awards/"

def get_mvp_voting_map(season):
    """
    Returns a list of maps of all the players that received MVP votes for the passed season. 

    :param season: The season from which a list of player voting maps will be returned.
    :return: A list of voting maps, where each element in the list is a map of how a given player received votes for the passed season.
    """
    url = BASE_URL + f"awards_{season}.html#mvp"

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    mvp_table = soup.find(id='mvp')

    return

