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

This notebook details the feature engineering techniques used in this project and provides code samples for each technique.

```python
import pandas as pd

example_df = pd.read_csv("../data/season_averages/2019_stats.csv")
```

## 1. Adding ranks to MVP recipients

### 1.1 Implementation 
Adding ranks to the MVP vote recipients is as simple as using the pandas `Series.rank` method:

```python
example_df["rank"] = example_df.points_won.rank(method="min", ascending=False)
```

Another important and desired trait of this field is for players who did not receive votes to have `NaN` as their rank. This way, the MVP vote recipients are can be easily accessed by filtering out the rows with `NaN` as a value in the `rank` field.

```python
example_df.loc[example_df.points_won == 0, "rank"] = float("nan")
```

```python
example_df.loc[~example_df["rank"].isna()]
```
