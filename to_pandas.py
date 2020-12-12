"""
Performs a conversion of a passed balldontlie JSON object to a pandas DataFrame.
"""

import pandas as pd
from query import *

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
