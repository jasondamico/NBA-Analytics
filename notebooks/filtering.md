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

# Filtering

This notebook details the thought process behind the filtering techniques used in this project and provies the code used to put these filters into use.

```python
import pandas as pd

season_average_dfs = []

for season in range (2000, 2021):
    try:
        file_name = f"../data/season_averages/{season}_stats.csv"
        df = pd.read_csv(file_name)

        season_average_dfs.append(df)
    except FileNotFoundError:
        pass
```

## 0. Identifying the problem

For each season that I plan on analyzing, over 400 players and their stats are available. However, only a select few of those players are even in the MVP conversation, and its rare to see any more than 5 players in pundet predictions for the MVP recipient at the end of the season. For that reason, the data can be significantly cleaned up of players irrelevant to the MVP conversation.

It's extremely difficult to quantify what makes a player in/out of the MVP conversation. Some general prerequisates for an MVP that would not be debated in NBA circles are as follows. Admittedly, these filters are conservative, but a large portion of the players in the data are removed by them. The candidate must:

1. Play at least 20 minutes/game
2. Consistently start for their team
3. Make the All-Star team (while this is admittedly somewhat arbitrary, STATS__________)

Another thing to note about filtering is that while it would be nice to filter down to only the "real" contenders (around 5 players for a given season), the players who *don't* receive votes are important data points as well (particularly in the context of training). Therefore, **my aim is to filter down to approximately 50 players for a given season**.


## 1. Filtering by win shares

One incredibly helpful tool for analysis are a player's win shares. According to [basketball-reference.com's page on the win share](https://www.basketball-reference.com/about/ws.html#:~:text=Win%20Shares%20is%20a%20player,the%20individuals%20on%20the%20team), this field is, in essence, the number of wins a given player contributes to his team. The field "is calculated using player, team and league-wide statistics and the sum of player win shares on a given team will be roughly equal to that team’s win total for the season". While this datapoint has the potential to be arbitrary, the methodology at least provides a ballpark.

**PROPOSAL: Filter out all players who are not in the top 50 win share players in a given season.**


### 1.1 Justification

To make sure that win shares was a good field to filter by, I decided to analyze the win share values of the player who won the MVP award in each of the years analyzed in this project. The code below displays the rank of each MVP over the last 20 years when sorting all players in the league by win shares:

```python
mvp_ws = []

num_first = 0
num_top_10 = 0

for i in range(len(season_average_dfs) - 1):    # does not include 2020-2021 data, as no MVP has been awarded yet
    mvp_index = season_average_dfs[i]["points_won"].idxmax()
    ws = season_average_dfs[i].ws.rank(ascending=False, method="max")[mvp_index]

    if ws == 1:
        num_first += 1
    if ws <= 10:
        num_top_10 += 1

    mvp_ws.append(ws)


print(mvp_ws, "\n")
print("MVPs that led the league in win shares:", num_first, f"({100 * num_first / len(mvp_ws)}%)")
print("MVPs that were in the top 10 of league win share getters:", num_top_10, f"({100 * num_top_10 / len(mvp_ws)}%)")
```

As can be seen, no MVP in the last 20 years has dropped below 15th in the league in win shares, the majority of MVPs are ranked in the top 10, and a bit more than half of MVPs led the league in win shares. 

The aim of the filtering is also to include players that are not necessarily MVPs, but their statistics and votes/lack of votes are also relevant. Thus, it's also worth analyzing if win shares are related to MVP votes. The analysis below analyzes whether or not each player that received MVP votes was in the top 50 of win share recipients in their given season (the proposed filter):

```python
mvp_ws = []

num_first = 0
num_top_10 = 0

outside_df = pd.DataFrame()

for i in range(len(season_average_dfs) - 1):    # does not include 2020-2021 data, as no MVP has been awarded yet
    vote_getters = season_average_dfs[i]
    vote_getters["ws_rank"] = vote_getters.ws.rank(ascending=False, method="max")

    vote_getters = vote_getters.loc[vote_getters["points_won"] > 0]
    
    num_in_top_50 = len(vote_getters.loc[vote_getters["ws_rank"] <= 50])
    num_outside = len(vote_getters.loc[vote_getters["ws_rank"] > 50])

    outside_df = outside_df.append(vote_getters.loc[vote_getters["ws_rank"] > 50])

    print(f"In top 50 WS: {num_in_top_50}", f"Outside: {num_outside} ({num_outside / len(vote_getters)}%)")
```

```python
outside_df.append(vote_getters.loc[vote_getters["ws_rank"] > 50]).points_won
```
