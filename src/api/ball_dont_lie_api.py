"""
A class to handle all methods related to interacting with the balldontlie API (https://www.balldontlie.io/).
"""

from .to_pandas import *

MAX_SEASON_STATS_IDS = 400

class BallDontLieAPI(BDLToPandas):

    def __init__(self):
        """ 
        Initializes a BallDontLieAPI object, complete wit the ability query and convert the results to a pandas DataFrame object.
        """
        BDLToPandas.__init__(self)

    def query(self, query_type=None, single_page=False, all_seasons=True, **query_params):
        """
        Performs a query of the passed type and returns the all data retrieved from the query.

        :param query_type: The type of query to be performed. Acceptable inputs are:
            - stats
            - players
            - games
            - season_stats
        :param single_page: A boolean corresponding to whether or not the user would like to query only a singular page of the API rather than accessing all pages available from the specified parameters. False by default.
        :param all_seasons: A boolean value representing whether or not all seasons should be accessed in the query. Exclusive to the "season_stats" query type.
        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions). NOTE: Only entering a singular query keyword parameter of `player_id` with an integer value will get a singular player.
        """
        if single_page:
            self.__single_page_query(query_type=query_type, **query_params)
        else:
            if query_type == "stats":
                self.query_all_stats(**query_params)
            elif query_type == "players":
                self.query_all_players(**query_params)
            elif query_type == "games":
                self.query_all_games(**query_params)
            elif query_type == "season_stats":
                start_season = None
                end_season = None

                if all_seasons:
                    start_season = FIRST_BDL_SEASON
                    end_season = CURRENT_NBA_SEASON

                self.query_all_season_stats(**query_params, start_season=start_season, end_season=end_season)

    def __single_page_query(self, query_type=None, **query_params):
        """
        Runs only the query specified, rather than storing the data accessed from all pages available from the passed query parameters.

        :param query_type: The type of query to be performed.
        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call.
        """
        if query_type == "stats":
            self.query_stats(**query_params)

    def get_json(self):
        """
        Returns the query result in the form of a JSON object.

        :return: A JSON object containing the result of the most recent API query.
        """
        return self.query_result

    def get_pandas_df(self):
        """
        Returns the pandas DataFrame equivalent of the held JSON object retrieved from the balldontlie API.

        :return: A pandas DataFrame object corresponding to the JSON data held by the most recent query.
        """
        return self.pandas_convert()

    def query_players_stats(self, players=None, all_seasons=True):
        """
        Queries the API to get the season stats of the players within the list passed to the `players` keyword.

        :param players: An array of player names. NOTE: For the most accurate results, use the full player name (e.g., enter ["Damian Lillard"] instead of ["Lillard"]).
        :param all_seasons: A boolean value representing whether or not all seasons should be accessed in the query.
        """
        if players:
            player_ids = self.__get_player_ids_from_search(players=players)
            
            self.query(query_type="season_stats", all_seasons=all_seasons, player_ids=player_ids)

    def __get_player_ids_from_search(self, players=None):
        """
        Returns a list of the player IDs of the players identified in the list passed through the `players` keyword. 

        :param players: An array of player names. NOTE: For the most accurate results, use the full player name (e.g., enter ["Damian Lillard"] instead of ["Lillard"]).
        :return: A list of the player IDs of the players held within the passed list. 
        """
        if players:
            player_ids = []

            for player in players:
                self.query(query_type="players", search=player)
                player_json = self.get_json()
                player_id = self.__get_player_id_from_json(player_json)

                player_ids.append(player_id)

        return player_ids

    def __get_player_id_from_json(self, player_json):
        """
        Returns the player ID from the JSON object passed.

        :param player_json: A JSON object representing a player.
        :return: The player ID held by the JSON object passed.
        """
        return player_json["data"][0]["id"]

    def get_all_player_ids(self):
        """
        Returns all of the player IDs present in the balldontlie API.

        :return: A list containing all of the player IDs (int) in the balldontlie API.
        """
        self.query(query_type="players")

        ids = []

        for i in range(len(self.data)):
            ids.append(self.data[i]["id"])

        return ids

    def load_full_season_stats(self, season):
        """
        Loads the season averages of all of the players who played in the passed season.
        
        :param season: The season from which season averages will be loaded.
        """
        ids = self.get_all_player_ids()
        num_players = len(ids)

        self.clear_data()

        # Without passing a smaller subset of the IDs list, the API returns a 414 error
        for i in range(0, num_players, MAX_SEASON_STATS_IDS):
            round_ids = ids[i:min(num_players + 1, i + 400)]
            self.query_all_season_stats(player_ids=round_ids, reset_data=False, season=season)
