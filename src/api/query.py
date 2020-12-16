"""
Handles queries of the balldontlie API and their related functions.
"""

import requests

stats_url = "https://www.balldontlie.io/api/v1/stats"
players_url = "https://www.balldontlie.io/api/v1/players"
games_url = "https://www.balldontlie.io/api/v1/games"
season_stats_url = "https://www.balldontlie.io/api/v1/season_averages"
array_fields = ["dates", "seasons", "player_ids", "game_ids"]

FIRST_BDL_SEASON = 1979
CURRENT_NBA_SEASON = 2020

class BDLQuery():

    params = {}
    data = []
    query_result = []

    def __init__(self):
        """
        Constructor method; creates a default BDLQuery object.
        """
        pass
    
    def __format_query_params(self, **query_params):
        """
        Formats the passed query parameters based on the accepted parameters of the balldontlie API.

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        for key, value in query_params.items():
            if key in array_fields:    
                self.params[key + "[]"] = value
            else:
                self.params[key] = value

    def query_stats(self, **query_params):
        """
        Stores the JSON object retrieved from passing the query parameters to the balldontlie statistics API.

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        self.__format_query_params(**query_params)

        r = requests.get(stats_url, params=self.params)

        self.query_result = r.json()

    def query_all_stats(self, **query_params):
        """
        Stores a modified JSON object containing all of the stats data from the passed query parameters (ignoring the starting page number).

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        self.__query_all_data(self.query_stats, **query_params)

    def __query_all_data(self, query_func, reset_data=True, **query_params):
        """
        Retrieves all the data from the specified query parameters by using the passed function and stores said data.

        :param query_func: The query function to be used to retrieve data.
        :param reset_data: A boolean representing whether or not the currently held data should be replaced with the present query (if TRUE) or extended with the present query (if FALSE).
        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        data = []

        self.params["page"] = 1
        self.params["per_page"] = 100

        query_func(**query_params)
        data.extend(self.query_result["data"])

        while(self.__update_page_request()):
            query_func(**query_params)
            data.extend(self.query_result["data"])

        if reset_data:
            self.data = data
        else:
            self.data.extend(data)

    def query_players(self, **query_params):
        """
        Stores the JSON object retrieved from passing the query parameters to the balldontlie players API.

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        self.__format_query_params(**query_params)

        r = requests.get(players_url, params=self.params)

        self.query_result = r.json()

    def query_all_players(self, **query_params):
        """
        Stores a modified JSON object containing all of the player data from the passed query parameters (ignoring the starting page number).

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        if self.is_single_player_query(**query_params):
            self.__clear_data()
            
            player_id = query_params["player_id"]
            url = players_url + f"/{player_id}"

            r = requests.get(url)

            self.data.append(r.json())
        else:
            self.__query_all_data(self.query_players, **query_params)

    def query_games(self, **query_params):
        """
        Stores the JSON object retrieved from passing the query parameters to the balldontlie games API.

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        self.__format_query_params(**query_params)

        r = requests.get(games_url, params=self.params)

        self.query_result = r.json()

    def query_all_games(self, **query_params):
        """
        Stores a modified JSON object containing all of the games data from the passed query parameters (ignoring the starting page number).

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        self.__query_all_data(self.query_games, **query_params)

    def query_season_stats(self, **query_params):
        """
        Stores the JSON object retrieved from passing the query parameters to the balldontlie season stats API.

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        self.__format_query_params(**query_params)

        r = requests.get(season_stats_url, params=self.params)

        self.query_result = r.json()

    def query_all_season_stats(self, start_season=None, end_season=None, **query_params):
        """
        Stores a modified JSON object containing all of the seasons stats data from the passed query parameters (ignoring the starting page number). Queries a range of seasons if a starting and ending season are specified.

        :param start_season: The first season to be queried.
        :param end_season: The final season to be queried.
        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        if start_season and end_season:
            self.__clear_data()

            for season in range(start_season, end_season + 1):
                self.__query_all_data(self.query_season_stats, reset_data=False, season=season, **query_params)
        else:
            self.__query_all_data(self.query_season_stats, **query_params)

    def __update_page_request(self):
        """
        Updates the page requested in the query parameters based on the next_page value stored within the passed JSON object.

        :return: The next page to be accessed. Returns None if the page limit is reached.
        """
        try:
            next_page = self.query_result["meta"]["next_page"]
        except KeyError:
            return None
        
        self.params["page"] = next_page
        return next_page

    def __clear_data(self):
        """
        Clears the instance variable holding a modified JSON object containing data from the queries.
        """
        self.data = []

    def is_single_player_query(self, **query_params):
        """
        Returns a boolean corresponding to whether or not the passed query parameters correspond to a single player query (only a singular parameter holding a player ID).

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        :return: TRUE if the query is for a singular player, FALSE otherwise.
        """
        return "player_id" in query_params and len(query_params) == 1
