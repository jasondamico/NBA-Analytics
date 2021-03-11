"""
Retrieves the advanced statistics of all the players in a given season via basketball-reference.com.
"""

from .bball_ref_utils import *

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_full_advanced_stats(season):
    """
    Returns a list containing the advanced stats of all of the players who played in the passed season.
        
    :param season: The season from which season averages will be returned.
    :return: A list of dictionaries holding the advanced statistics of all the players in the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"NBA_{season}_advanced.html"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find(id="advanced_stats")
    trs = table.find_all("tr", {"class":["full_table", "partial_table"]})

    return get_rows_dict(trs)
