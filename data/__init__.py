"""
File used to automatically download and save CSV files of data when the `data` library is imported into a project. 
"""

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from .load_data import download_mvp_stats

download_mvp_stats()
