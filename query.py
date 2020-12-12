"""
Handles queries of the balldontlie API and their related functions.
"""

import requests

stats_url = "https://www.balldontlie.io/api/v1/stats"
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
        :return: The JSON object returned when the passed query parameters are used in the balldontlie API.
        """
        self.__format_query_params(**query_params)

        r = requests.get(stats_url, params=self.params)

        self.query_result = r.json()

    def query_all_stats(self, **query_params):
        """
        Stores a modified JSON object containing all of the data from the passed query parameters (ignoring the starting page number).

        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        data = []

        self.params["page"] = 1

        self.query_stats(**query_params)
        data.extend(self.query_result["data"])

        while(self.__update_page_request()):
            self.query_stats(**query_params)
            data.extend(self.query_result["data"])

        self.data = data

    def __update_page_request(self):
        """
        Updates the page requested in the query parameters based on the next_page value stored within the passed JSON object.
        """
        next_page = self.query_result["meta"]["next_page"]
        self.params["page"] = next_page

        return next_page
