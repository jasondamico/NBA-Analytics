"""
Module containing functions related to loading and saving CSV files of player data and season averages.
"""

import pandas as pd
import os.path

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from api import ball_dont_lie_api
import scraping.basketball_reference.mvp_votes as mvp_votes

BDL = ball_dont_lie_api.BallDontLieAPI()

CURRENT_SEASON = 2020
FIRST_SEASON = 2000

def download_mvp_stats():
    """
    Loads all of the data needed for MVP analysis.
    """
    print("Beginning load MVP stats...")

    bdl = ball_dont_lie_api.BallDontLieAPI()

    player_map = None
    map_df = None

    for season in range(FIRST_SEASON, CURRENT_SEASON + 1):
        name = str(season) + "_stats.csv"

        csv_dir = os.path.join(currentdir, "season_averages")

        check_dir(csv_dir)

        complete_name = os.path.join(csv_dir, name)

        if not csv_exists(complete_name):
            # loads player_map, converts to a df if that has not been done yet
            if not player_map and not map_df:
                player_map = bdl.get_player_name_map()
                map_df = pd.DataFrame.from_dict(player_map, orient="index", columns=["last_name", "first_name", "team_name"])

            bdl.load_full_season_stats(season)
            df = bdl.get_pandas_df()

            merged = pd.merge(map_df, df, how="right", left_index=True, right_on="player_id")
           
            if season != CURRENT_SEASON:
                merged = get_appended_votes_df(merged, season)
            else:
                # In absence of appending MVP votes, the same columns are filled with NaN for the current season
                merged.loc[:, mvp_votes.RELEVANT_COL_NAMES] = float("NaN")

            drop_duplicate_cols(merged)

            merged.to_csv(complete_name, index=False)

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

    :param dir_path: A directory path that will be created if it does not already exist.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def get_appended_votes_df(stats_df, season):
    """
    Returns a DataFrame object identical to the one passed as an argument, but with the MVP voting stats from the passed season appended to the listed.

    :param stats_df: A DataFrame object containing NBA season average statistics.
    :param season: An integer value representing the season from which MVP voting should be retrieved. For instance, an inputted season value of 2019 returns the voting record from the 2019-2020 season. 
    :return: An identical DataFrame object to the one passed, but with MVP voting stats for the passed season appended.
    """
    voting_maps_list = mvp_votes.get_mvp_voting_map(season)
    voting_maps_df = pd.DataFrame(voting_maps_list)

    stats_df["full_name"] = stats_df["first_name"] + " " + stats_df["last_name"]

    df_with_votes = pd.merge(stats_df, voting_maps_df, how="left", left_on="full_name", right_on="player")

    df_with_votes.loc[:, mvp_votes.RELEVANT_COL_NAMES] = df_with_votes.loc[:, mvp_votes.RELEVANT_COL_NAMES].fillna(value=0)

    return df_with_votes

def drop_duplicate_cols(stats_df):
    """
    Drops all columns in the passed DataFrame that were duplicate and/or created in order to properly assemble the DataFrame, but are no longer needed.

    :param stats_df: A DataFrame object containing NBA season average statistics.
    """
    # Uses set's intersection method to only drop the columns present in the stats_df columns (thus avoiding  an error relating to trying to drop a column that doesn't exist)
    intersection_list = list(set(stats_df.columns).intersection(["full_name", "player"]))

    stats_df.drop(intersection_list, axis=1, inplace=True)
