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
    "Grade":[90.3, "91", "89.2", 95]
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

This gets us part of the way there: both `Age` and `Grade` were converted to their expected data types (`int64` and `float64`, respectively), despite the fact that mixed data types were stored in each array. However, as can be seen, the `Name` column is converted to type `float64` when using a keyword argument of `coerce`, which is necessary to convert strings with decimal values to floats. Ideally, these values should be kept the same; there is no need to convert *non*-number-like strings to numeric values. 

We will use `fillna` to fill the `NaN` values with their original value in the following function:

```python
def convert_col_types(column):
    """
    Given a passed column from the season averages data with all string values, converts all number-like strings to floats or integers and returns a column holding the converted values. If a value stored is not number-like, then the original string value is still kept in its corresponding index.

    :param column: An unformatted Series object representing the column of a NBA season average statistics DataFrame.
    :return: A column with all number-like values in the passed columns converted to either integers or floats, with all other strings retaining their original value.
    """
    to_return_col = pd.to_numeric(column, errors="coerce")      # Converts all strings containing number-like values to floats or integers. All other values are filled with NaN
    to_return_col = to_return_col.fillna(column)    # Fills all NaN values with their value from the original column
    
    return to_return_col
```

```python
df_final = df.apply(lambda column: convert_col_types(column))
display(df_final, df_final.dtypes)
```

And, simple as that, the desired result is achieved: the `Age` and `Grade` columns are converted to `int64` and `float64`, respectively, while `Name` retains its original data type. Feature engineering may proceed.
