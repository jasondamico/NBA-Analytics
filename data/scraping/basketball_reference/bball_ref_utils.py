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
