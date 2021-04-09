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

## 0. Convert all values from number-like strings to floats/integers

Before doing any feature engineering, it must be noted that the data stored in the CSV files are all strings, as the values are scraped from the HTML source and stored directly in the DataFrame. Thus, doing any feature engineering on the unformatted DataFrame would prove futile. The conversion is relatively simple via a `lambda` function and `DataFrame.apply()`. Please note that while this is necessary when feature engineering prior to exporting the DataFrame to a CSV file, the process of exporting seems to make this conversion automatically upon export. An example DataFrame is used as a proof of concept.

```python
data = {
    "Name":["Peter", "Paul", "Trisha", "Joseph"],
    "Age":["20", "21", "19", "18"],
    "Grade":[90.3, "91", "89.2", 95],
    "GPA":["87.5", "", "94.5", "90.0"]
}

df = pd.DataFrame(data)
```

```python
display(df, df.dtypes)
```

### 0.1 Implementation

The first thing to do is convert all values to numeric values using `pd.to_numeric`:

```python
df_to_numeric = df.apply(lambda column: pd.to_numeric(column, errors="coerce"))
display(df_to_numeric, df_to_numeric.dtypes)
```

This gets us part of the way there: `Age`, `Grade` and `GPA` were converted to their expected data types (`int64` and `float64`, respectively), despite the fact that mixed data types were stored in each array. However, as can be seen, the `Name` column is converted to type `float64` when using a keyword argument of `coerce`, which is necessary to convert strings with decimal values to floats. Ideally, these values should be kept the same; there is no need to convert *non*-number-like strings to numeric values. 

We will use `fillna` to fill the `NaN` values with their original value in the following function:

```python
df_to_numeric = df.apply(lambda column: pd.to_numeric(column, errors="coerce").fillna(column))
display(df_to_numeric, df_to_numeric.dtypes)
```

Unfortunately, we still have one holdout column: `GPA`, the column that included an empty string, which the converter function still thinks is an entire column of strings. However, we still want to preserve the `fillna()` functionality for columns that *actually* are only full of strings, so we will add a conditional statement to preserve columns that are a mix of floats and strings:

```python
def convert_col_types(column):
    """
    Given a passed column from the season averages data with all string values, converts all number-like strings to floats or integers and returns a column holding the converted values. If a value stored is not number-like, then the original string value is still kept in its corresponding index.

    :param column: An unformatted Series object representing the column of a NBA season average statistics DataFrame.
    :return: A column with all number-like values in the passed columns converted to either integers or floats, with all other strings retaining their original value.
    """
    to_return_col = pd.to_numeric(column, errors="coerce")      # Converts all strings containing number-like values to floats or integers. All other values are filled with NaN
    if to_return_col.isna().sum() == len(to_return_col):    # Only performs `fillna()` for columns that are full of NaN values, or columns full of non number-like strings
        to_return_col = to_return_col.fillna(column)    # Fills all NaN values with their value from the original column
    
    return to_return_col
```

```python
df_final = df.apply(lambda column: convert_col_types(column))
display(df_final, df_final.dtypes)
```

And, simple as that, the desired result is achieved: the `Age`, `Grade` and `GPA` columns are converted to `int64`, `float64` and `float64`, respectively, while `Name` retains its original data type. Feature engineering may proceed.


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

## 2. Scaling major season averages fields

While raw season averages are important for analysis, it must be noted that MVP voting is based purely on the performance of players over the course of the season that voting occurs. Therefore, all player performances over the course of a single season are compared to one another to determine who is most worthy of MVP votes.

### 2.1 Implementation

To reflect this convention within this project, scaled fields are scaled on a 0-1 scale proportional to the distribution of players within that field. 

For instance, in 2019, James Harden led the league with 34.3 points per game, so his scaled points per game value for the 2019 season would be 1. Any other player would have a scaled points per game value relative to his performance compared to that of the league leader (their points per game value divided by the points per game value of Harden).

While we note that we can manually get the maximum value of each column, effectively getting the league leader, we instead use the `data.scraping.basketball_reference.league_leaders` library to retrieve the league leader from the given field, as [basketball-reference.com takes accepted conventions such as minimum attempts into account when selecting the league leader for a given field](https://www.basketball-reference.com/about/rate_stat_req.html).

```python
import sys
sys.path.insert(1, "../")
import data.scraping.basketball_reference.league_leaders as league_leaders
```

```python
league_leader_id = league_leaders.get_league_leader(2019, "pts_per_g")["player_id"]
example_df.loc[example_df["id"] == league_leader_id, ["id", "player", "team_id", "pts_per_g"]]
```

The following function takes an argument of `field`, which is used to determine the league leader and then scale the remaining values.

Note that if the passed field is not found on the basketball-reference.com league leaders page for the season specified, then a custom error of `FieldNotFound` is raised. In this case (which is only for the more obscure data fields), the exception is caught and the maximum value of the passed field is used as the league leader value.

```python
def scale_field(stats_df, season, field):
    try:
        league_leader_value = league_leaders.get_league_leader(season, field)["value"]
    except league_leaders.FieldNotFound:    # Some fields are not found on the basketball-reference.com league leaders page, exception raised in this case
        league_leader_value = stats_df[field].max()
    stats_df[f"scaled_{field}"] = stats_df[field] / league_leader_value   # league leader has value of 1, all other rows are a decimal value in range [0, 1)
    
scale_field(example_df, 2019, "pts_per_g")
```

For example, Celtics player Jaylen Brown, who averaged 20.3 points per game in 2019, would have a scaled points per game value of 0.592 (20.3 / 34.3).

```python
jaylen_id = example_df.loc[example_df["player"] == "Jaylen Brown"].id.tolist()[0]
example_df.loc[example_df["id"].isin([league_leader_id, jaylen_id]), ["id", "player", "team_id", "pts_per_g", "scaled_pts_per_g"]]
```
