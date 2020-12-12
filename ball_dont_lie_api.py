"""
A class to handle all methods related to interacting with the balldontlie API (https://www.balldontlie.io/).
"""

from to_pandas import *

class BallDontLieAPI(BDLToPandas):

    def __init__(self):
        """ 
        Initializes a BallDontLieAPI object, complete wit the ability query and convert the results to a pandas DataFrame object.
        """
        BDLToPandas.__init__(self)

    def query(self, query_type=None, single_page=False, **query_params):
        """
        Performs a query of the passed type and returns the all data retrieved from the query.

        :param query_type: The type of query to be performed. Acceptable inputs are:
            - stats
            - players
        :param single_page: A boolean corresponding to whether or not the user would like to query only a singular page of the API rather than accessing all pages available from the specified parameters. False by default.
        :param **query_params: Keyword arguments corresponding to parameters to be used in the API call (see https://www.balldontlie.io/ for more details on parameter conventions).
        """
        if single_page:
            self.__single_page_query(query_type=query_type, **query_params)
        else:
            if query_type == "stats":
                self.query_all_stats(**query_params)
            elif query_type == "players":
                self.query_all_players(**query_params)

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
