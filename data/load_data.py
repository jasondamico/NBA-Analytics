"""
Module containing functions related to loading and saving CSV files of player data and season averages.
"""

import pandas as pd
import numpy as np
import os.path

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import scraping.basketball_reference.mvp_votes as mvp_votes
import scraping.basketball_reference.team_records as team_records
import scraping.basketball_reference.season_averages as season_averages
import scraping.basketball_reference.advanced_stats as advanced_stats
import scraping.basketball_reference.league_leaders as league_leaders

CURRENT_SEASON = 2020
FIRST_SEASON = 2000
SIGNIFICANT_STAT_CATEGORIES = ["pts_per_g", "ast_per_g", "trb_per_g", "blk_per_g", "stl_per_g"]

def download_mvp_stats():
    """
    Loads all of the data needed for MVP analysis.
    """
    print("Beginning load MVP stats...")

    for season in range(FIRST_SEASON, CURRENT_SEASON + 1):
        name = str(season) + "_stats.csv"

        csv_dir = os.path.join(currentdir, "season_averages")

        check_dir(csv_dir)

        complete_name = os.path.join(csv_dir, name)

        if not csv_exists(complete_name):
            df = season_averages.get_full_season_stats_df(season)
           
            if season != CURRENT_SEASON:
                df = get_appended_votes_df(df, season)
            else:
                # In absence of appending MVP votes, the same columns are filled with NaN for the current season
                df.loc[:, mvp_votes.RELEVANT_COL_NAMES] = float("NaN")

            df = get_team_record_df(df, season)
            df = get_advanced_stats_df(df, season)
            df = get_league_leaders_df(df, season)

            df.to_csv(complete_name, index=False)

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

    df_with_votes = pd.merge(stats_df, voting_maps_df, how="left")

    df_with_votes.loc[:, mvp_votes.RELEVANT_COL_NAMES] = df_with_votes.loc[:, mvp_votes.RELEVANT_COL_NAMES].fillna(value=0)

    return df_with_votes

def get_team_record_df(stats_df, season):
    """
    Returns a DataFrame object identical to the one passed as an argument, but with the record of the team each player played for in the passed season appended to the DataFrame.

    :param stats_df: A DataFrame object containing NBA season average statistics.
    :param season: An integer value representing the season from which MVP voting should be retrieved. For instance, an inputted season value of 2019 returns the voting record from the 2019-2020 season. 
    :return: An identical DataFrame object to the one passed, but with team winning percentages for the passed season appended.
    """
    record = team_records.get_team_record_map(season)
    record_df = pd.DataFrame.from_dict(record, orient="index", columns=["winning_perc"])

    return pd.merge(stats_df, record_df, how="left", left_on="team_id", right_index=True)

def get_advanced_stats_df(stats_df, season):
    """
    Returns a DataFrame object identical to the one passed as an argument, but with the advanced season stats of each player who played in the passed season appended to the DataFrame.

    :param stats_df: A DataFrame object containing NBA season average statistics.
    :param season: An integer value representing the season from which MVP voting should be retrieved. For instance, an inputted season value of 2019 returns the voting record from the 2019-2020 season. 
    :return: An identical DataFrame to the one passed, but with the advanced season stats for the passed season appended.
    """
    advanced_stats_df = advanced_stats.get_full_advanced_stats_df(season)
    cols_to_use = ["id"] + advanced_stats_df.columns.difference(stats_df.columns).to_list()
    
    return pd.merge(stats_df, advanced_stats_df[cols_to_use], how="left")

def get_league_leaders_df(stats_df, season):
    """
    Returns a DataFrame object identical to the one passed as an argument, but with binary fields corresponding to whether or not each player led the league in a significant stat category.

    :param stats_df: A DataFrame object containing NBA season average statistics.
    :param season: An integer value representing the season from which MVP voting should be retrieved. For instance, an inputted season value of 2019 returns the voting record from the 2019-2020 season. 
    :return: An identical DataFrame to the one passed, but with binary fields corresponding to whether or not each player led the league in a significant stat category appended.
    """
    to_return_df = stats_df
    
    league_leaders_df = league_leaders.get_full_league_leaders_df(season, SIGNIFICANT_STAT_CATEGORIES)
    fields = league_leaders_df.field.unique().tolist()

    for field in fields:
        player_id = league_leaders_df.loc[league_leaders_df["field"] == field, "player_id"].item()
        stats_df[f"leader_{field}"] = np.where(stats_df.id == player_id, 1, 0)

    return to_return_df

def drop_duplicate_cols(stats_df):
    """
    Drops all columns in the passed DataFrame that were duplicate and/or created in order to properly assemble the DataFrame, but are no longer needed.

    :param stats_df: A DataFrame object containing NBA season average statistics.
    """
    # Uses set's intersection method to only drop the columns present in the stats_df columns (thus avoiding  an error relating to trying to drop a column that doesn't exist)
    intersection_list = list(set(stats_df.columns).intersection(["full_name", "player"]))

    stats_df.drop(intersection_list, axis=1, inplace=True)
