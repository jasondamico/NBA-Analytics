"""
Module containing functions related to loading and saving CSV files of player data and season averages.
"""

import pandas as pd
import os.path

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from src.api import ball_dont_lie_api

BDL = ball_dont_lie_api.BallDontLieAPI()

CURRENT_SEASON = 2020
FIRST_SEASON = 2000

def download_mvp_stats():
    """
    Loads all of the data needed for MVP analysis.
    """
    print("Beginning load MVP stats...")

    bdl = ball_dont_lie_api.BallDontLieAPI()

    player_map = bdl.get_player_name_map()
    map_df = pd.DataFrame.from_dict(player_map, orient="index", columns=["last_name", "first_name"])

    for season in range(FIRST_SEASON, CURRENT_SEASON + 1):
        name = str(season) + "_stats.csv"

        csv_dir = os.path.join(currentdir, "season_averages")

        check_dir(csv_dir)

        complete_name = os.path.join(csv_dir, name)

        if not csv_exists(complete_name):
            bdl.load_full_season_stats(season)
            df = bdl.get_pandas_df()

            merged = pd.merge(map_df, df, how="right", left_index=True, right_on="player_id")
            merged.to_csv(complete_name)

    print("Completed load MVP stats.")

def csv_exists(csv_name):
    """
    Returns a boolean corresponding to whether or not a CSV file of the passed name has already been created.

    :param csv_name: The name of a CSV that will be checked for existence.
    :return: TRUE if a CSV file of the passed name exists, FALSE otherwise.
    """
    return os.path.isfile(csv_name)

def check_dir(dir_path):
    """
    Checks to see if the passed directory path exists, creates it if not.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
