"""
Retrieves the team a group of players played on in a specified season according to basketball-reference.com
"""

from bball_ref_utils import *
from team_abbreviation_dict import team_abbreviation_dict

BASE_URL = "https://www.basketball-reference.com/leagues/"

def get_player_team_map(season):
    """
    Given a passed season, returns a map of player names and the team they played for in that season.

    :param season: The season from which a map of team records will be returned.
    :return: A map linking team names to the record they had in the passed season.
    """
    season = convert_bdl_season_to_bball_ref(season)

    url = BASE_URL + f"NBA_{season}_per_game.html"

    page = requests.get(url)

    check_status_code(page, season)

    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find(id="per_game_stats")
    trs = table.find_all("tr", {"class":["full_table", "partial_table"]})

    return get_rows_dict(trs)

def get_rows_dict(trs):
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
            player = {}

            for td in tr.find_all("td"):    # Scrapes and stores data related to the player in this row
                data_type = td.get("data-stat")
                if data_type == "player":
                    player["id"] = td.get("data-append-csv")    # A unique identifier used by basketball-reference.com
                
                player[data_type] = td.get_text()

            player["multi_team_player"] = 0
        else:   # Initializes multiple team handling sequence
            player["multi_team_player"] = 1
            stored_team_games = int(player["g"])
            current_row_games_played = int(tr.find_all("td", {"data-stat":"g"})[0].get_text())

            if player["team_id"] == "TOT" or current_row_games_played > stored_team_games:      # NOTE: The statistics of the player stored are their total season stats, but the team stored is the team they played the most games for
                current_row_team = tr.find_all("td", {"data-stat":"team_id"})[0].get_text()
                player["g"] = current_row_games_played
                player["team_id"] = current_row_team

    return players
