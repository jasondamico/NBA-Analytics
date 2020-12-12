"""
Handles queries of the balldontlie API and their related functions.
"""

import requests

stats_url = "https://www.balldontlie.io/api/v1/stats"
players_url = "https://www.balldontlie.io/api/v1/players"
games_url = "https://www.balldontlie.io/api/v1/games"
array_fields = ["dates", "seasons", "player_ids", "game_ids"]

class BDLQuery():

    def __init__(self):
        """
        Constructor method; creates a BallDontLieAPI object.
        """
        self.params = {}
        self.data = []
        self.query_result = []
    
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

    def __query_all_data(self, query_func, **query_params):
        """
        Retrieves all the data from the specified query parameters by using the passed function and stores said data.

        :param func: The query function to be used to retrieve data.
        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        data = []

        self.params["page"] = 1

        query_func(**query_params)
        data.extend(self.query_result["data"])

        while(self.__update_page_request()):
            query_func(**query_params)
            data.extend(self.query_result["data"])

        self.data = data

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

    def __update_page_request(self):
        """
        Updates the page requested in the query parameters based on the next_page value stored within the passed JSON object.
        """
        next_page = self.query_result["meta"]["next_page"]
        self.params["page"] = next_page

        return next_page
