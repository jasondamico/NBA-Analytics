"""
Retrieves the team a group of players played on in a specified season according to basketball-reference.com
"""

from bball_ref_utils import *

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

    for tr in trs:
        team = tr.find_all("td", {"data-stat":"team_id"})[0].get_text()
        name = tr.find_all("td", {"data-stat":"player"})[0].get_text()

        player_team_map[name] = team

    return player_team_map
