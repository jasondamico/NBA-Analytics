"""
Holds objects that represent a season of NBA data.
"""

import pandas as pd

class NBAData():

    def __init__(self, season):
        self.__season = season
        self.__df = pd.DataFrame()
