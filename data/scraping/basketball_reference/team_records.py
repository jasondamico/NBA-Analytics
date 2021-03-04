"""
Performs web scraping of NBA team records.
"""

from .bball_ref_utils import *

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_team_record_map(season):
    """
    Returns a map correlating a team name with their record for the passed season.

    :param season: The season from which a map of team records will be returned.
    :return: A map linking team names to the record they had in the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"NBA_{season}.html"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')

    if season >= 2015:
        east_table = soup.find(id='confs_standings_E')
        west_table = soup.find(id='confs_standings_W')
    else:
        east_table = soup.find(id='divs_standings_E')
        west_table = soup.find(id='divs_standings_W')

    # tuple holding both table objects for ease of further scraping
    record_tables = (east_table, west_table)

    record_map = {}

    for table in record_tables:
        ths = table.find_all('th')
        tds = table.find_all('td')

        valid_ths = __get_relevant_ths(ths)

        valid_tds = __get_relevant_tds(tds)

        for i in range(len(valid_tds)):
            # Since the scraping moves from the top of the page to the bottom, each index corresponds to a row in the conference table. Thus, team name and record are at the same index in their respective lists.
            td = valid_tds[i]
            th = valid_ths[i]

            team_id = __get_team_id(th)
            team_record = float(td.get_text())

            record_map[team_id] = team_record

    return record_map

def __get_relevant_ths(ths):
    """
    Based on a list of th tags passed, returns a list of "relevant" th tags, meaning tags that hold the name of a team.

    :param ths: A list of th tags scraped from basketball-reference.com.
    :return: A list of ths tags relevant for analysis (that hold the name of an NBA team).
    """
    valid_ths = []

    for th in ths:
        if th.get("data-stat") == "team_name" and not th.get("aria-label"):
            valid_ths.append(th)

    return valid_ths

def __get_relevant_tds(tds):
    """
    Based on a list of td tags passed, returns a list of "relevant" td tags, meaning tags that hold a team's record.

    :param tds: A list of td tags scraped from basketball-reference.com.
    :return: A list of td tags relevant for analysis (that hold the record of an NBA team).
    """
    valid_tds = []

    for td in tds:
        if td.get("data-stat") == "win_loss_pct":
            valid_tds.append(td)

    return valid_tds

def __get_team_id(th):
    """
    Returns the three-letter team ID from the passed th tag.

    :th: A th tag holding the name of an NBA team.
    :return: The three-letter team ID that basketball-reference.com uses to identify the team.
    """
    url = str(th.find("a").get("href"))
    team_id = url.replace("/teams/", "").split("/", 1)[0]     # Taking the three-letter team ID from the link to the team's individual page for the season

    return team_id
