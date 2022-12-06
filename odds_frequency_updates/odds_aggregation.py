#%%
from typing import Any, Dict

from pymongo import MongoClient
import pandas as pd

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.22.48.1:27017")
db = client["cs415_production"]
odds_coll_names = [
    col_name
    for col_name in db.list_collection_names()
    if col_name.startswith("odds_") and col_name != "odds_api_keys"
]

betting_types = ["h2h", "outrights", "spreads", "totals"]

count_dict = {}

for bet_type in betting_types:
    for coll_name in odds_coll_names:
        result = list(
            db[coll_name].aggregate(
                [
                    {
                        "$unwind": {
                            "path": f"${bet_type}",
                            "preserveNullAndEmptyArrays": False,
                        }
                    },
                    {
                        "$project": {
                            f"{bet_type}_update_at": {
                                "$dateToString": {
                                    "date": f"${bet_type}.saved_at",
                                    "format": "%Y-%m-%dT%H:00:00Z",
                                    "timezone": "America/New_York",
                                }
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": {
                                "$dateFromString": {
                                    "dateString": f"${bet_type}_update_at"
                                }
                            },
                            f"{bet_type}_count": {"$sum": 1},
                        }
                    },
                ]
            )
        )

        for entry in result:
            if entry["_id"] not in count_dict:
                count_dict[entry["_id"]] = 0
            count_dict[entry["_id"]] += entry[f"{bet_type}_count"]
        

# for entry in count_dict:
#   print(entry, count_dict[entry])
odds_agg_df = pd.Series(count_dict)

game_times = list(db['nfl_games'].aggregate([
    {
        '$project': {
            '_id': '$timestamp'
        }
    }
]))

game_times = pd.array([pd.Timestamp(d['_id']) for d in game_times])

%store df
%store game_times

# %%
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np

sns.set_theme(style="whitegrid")
ax = sns.lineplot(odds_agg_df)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
plt.tight_layout()

xmin, xmax = ax.get_xlim()
days = np.arange(np.floor(xmin), np.ceil(xmax)+2) # range of days in date units
weekends = [(dt.weekday()>=6)|(dt.weekday()==0) for dt in mdates.num2date(days)]
ax.set_xlim(xmin, xmax) # set limits back to default values
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.set_xlabel("Date")
ax.set_ylabel("Aggregated Odds Updates (per hour)")
ax.set_title("Aggregated Betting Odds Update Frequency")
for time in game_times.unique():
  ax.axvline(x=time, color='red', linestyle=':', alpha=0.5)
ax.fill_between(days, *ax.get_ylim(), where=weekends, facecolor='k', alpha=.125)
ax.set_xlim(xmin=xmin+1, xmax=xmax-1)
plt.show()

# %%
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np

sns.set_theme(style="whitegrid")
ax = sns.lineplot(odds_agg_df)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
plt.tight_layout()

xmin, xmax = ax.get_xlim()
days = np.arange(np.floor(xmin), np.ceil(xmax)+2) # range of days in date units
weekends = [(dt.weekday()>=6)|(dt.weekday()==0) for dt in mdates.num2date(days)]
ax.set_xlim(xmin, xmax) # set limits back to default values
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.set_xlabel("Time")
ax.set_ylabel("Aggregated Odds Updates (per hour)")
ax.set_title("Aggregated Betting Odds Update Frequency")
for time in game_times.unique():
  ax.axvline(x=time, color='red', linestyle=':', alpha=0.5)
ax.fill_between(days, *ax.get_ylim(), where=weekends, facecolor='k', alpha=.125)
ax.set_xlim(xmin=xmin+1, xmax=xmax-1)
plt.legend(loc='lower right', labels=['Total Bet Updates', 'Sundays', 'NFL Game'])
plt.show()


# %%
