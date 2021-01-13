"""
Performs a conversion of a passed balldontlie JSON object to a pandas DataFrame.
"""

import pandas as pd
from .query import *

# Objects held within query results
objects = ["player", "game", "team", "home_team", "visitor_team"]

class BDLToPandas(BDLQuery):

    def __init__(self):
        """
        Constructor method; creates a BDLToPandas object based on the passed bdl_data value.

        :param bdl_data: A JSON object containing data retrieved from the balldontlie API service that is to be converted to a pandas df.
        """
        BDLQuery.__init__(self)
        self.pandas_df = []

    def pandas_convert(self):
        """
        Converts the held balldontlie JSON object to a pandas DataFrame and returns the newly created DataFrame.

        :return: A pandas DataFrame representing the balldontlie JSON object held by the object.
        """
        data = {}

        for names in self.data[0]:
            col_values = []

            if names in objects:
                for items in self.data[0][names]:
                    col_values = []

                    col_name = names + "_" + items

                    for i in range(len(self.data)):
                        col_values.append(self.data[i][names][items])

                    data[col_name] = col_values
            else:
                for i in range(len(self.data)):
                    col_values.append(self.data[i][names])
            
                data[names] = col_values

        return pd.DataFrame(data=data)

    
    def get_player_name_map(self, using_stored_data=False):
        """
        Returns a map of the player IDs currently held to a list holding the player's name (in the format of [last, first]).

        :param using_stored: A boolean indicating if the returned map should be a map of the players stored (when value is TRUE), or a map of all players available in the database (when value is FALSE).
        :return: A dictionary in which the keys are all unique player IDs and each value is an array holding the name of the corresponding player ID in the format [last, first].
        """
        name_map = {}

        temp = self.data
        
        if not using_stored_data:
            # creates a map using all player IDs in the database
            self.query_all_players()

            for player in self.data:
                player_id = player["id"]

                player_first = player["first_name"]
                player_last = player["last_name"]

                name_map[player_id] = [player_last, player_first]
        else:
            # creates a map using only the stored player IDs
            player_ids = set()

            for item in self.data:
                try:
                    player_id = item["player_id"]
                    player_ids.add(player_id)
                except KeyError:    # if item does not have a player_id key and, therefore, is not a player
                    pass

            for player_id in player_ids:
                self.query_all_players(player_id=player_id)
                player = self.data

                player_first = player[0]["first_name"]
                player_last = player[0]["last_name"]

                name_map[player_id] = [player_last, player_first]

        self.data = temp

        return name_map

