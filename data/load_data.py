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

