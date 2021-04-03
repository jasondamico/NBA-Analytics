---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.8.0
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Feature Engineering

This notebook details the feature engineering techniques used in this project and provides code samples for each technique. All methods discussed this notebooks are applied to the data in the `get_feature_engineered_df()` function found in `data/load_data.py`.

```python
import pandas as pd

example_df = pd.read_csv("../data/season_averages/2019_stats.csv")
```
