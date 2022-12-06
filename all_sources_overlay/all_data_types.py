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

odds_count_dict = {}

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
            if entry["_id"] not in odds_count_dict:
                odds_count_dict[entry["_id"]] = 0
            odds_count_dict[entry["_id"]] += entry[f"{bet_type}_count"]
    
# for entry in count_dict:
#   print(entry, count_dict[entry])
odds_agg_df = pd.Series(odds_count_dict)

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
from typing import Any, Dict

from pymongo import MongoClient
import pandas as pd

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.22.48.1:27017")
db = client["cs415_production"]
reddit_nfl_coll_names = ["reddit_stream_submissions", "reddit_stream_comments"]

reddit_nfl_count_dict = {}

for coll_name in reddit_nfl_coll_names:
    result = list(db[coll_name].aggregate([
            {
                '$match': {
                    'subreddit': {
                        '$in': [
                            '49ers', 'AZCardinals', 'Browns', 'CHIBears', 'Chargers', 'Colts', 'DenverBroncos', 'GreenBayPackers', 'Jaguars', 'KansasCityChiefs', 'NYGiants', 'Patriots', 'Redskins', 'Saints', 'Seahawks', 'StLouisRams', 'Tennesseetitans', 'Texans', 'bengals', 'buccaneers', 'buffalobills', 'cowboys', 'detroitlions', 'eagles', 'falcons', 'miamidolphins', 'minnesotavikings', 'nyjets', 'oaklandraiders', 'panthers', 'ravens', 'steelers'
                        ]
                    }
                }
            }, {
                '$project': {
                    'created_at': {
                        '$dateTrunc': {
                            'date': '$created_at', 
                            'unit': 'minute', 
                            'binSize': 60, 
                            'timezone': 'America/New_York'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$created_at', 
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]))

    for entry in result:
        if entry["_id"] not in reddit_nfl_count_dict:
            reddit_nfl_count_dict[entry["_id"]] = 0
        reddit_nfl_count_dict[entry["_id"]] += entry["count"]

reddit_nfl_agg_df = pd.Series(reddit_nfl_count_dict)
reddit_nfl_agg_df = reddit_nfl_agg_df.resample('H').sum()

%store reddit_nfl_agg_df

# %%
from typing import Any, Dict

from pymongo import MongoClient
import pandas as pd

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.22.48.1:27017")
db = client["cs415_production"]
reddit_coll_names = ["reddit_stream_submissions", "reddit_stream_comments"]

reddit_count_dict = {}

for coll_name in reddit_coll_names:
    result = list(db[coll_name].aggregate([
            {
                '$project': {
                    'created_at': {
                        '$dateTrunc': {
                            'date': '$created_at', 
                            'unit': 'minute', 
                            'binSize': 60, 
                            'timezone': 'America/New_York'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$created_at', 
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]))

    for entry in result:
        if entry["_id"] not in reddit_count_dict:
            reddit_count_dict[entry["_id"]] = 0
        reddit_count_dict[entry["_id"]] += entry["count"]

reddit_agg_df = pd.Series(reddit_count_dict)

%store reddit_agg_df

# %%
from typing import Any, Dict

from pymongo import MongoClient
import pandas as pd

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.27.80.1:27017")
db = client["cs415_production"]
twitter_coll_names = ["twitter_stream"]

twitter_count_dict = {}

for coll_name in twitter_coll_names:
    result = list(db[coll_name].aggregate([
            {
                '$project': {
                    'created_at': {
                        '$dateTrunc': {
                            'date': '$created_at', 
                            'unit': 'minute', 
                            'binSize': 60, 
                            'timezone': 'America/New_York'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$created_at', 
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]))

    for entry in result:
        if entry["_id"] not in twitter_count_dict:
            twitter_count_dict[entry["_id"]] = 0
        twitter_count_dict[entry["_id"]] += entry["count"]

twitter_agg_df = pd.Series(twitter_count_dict).fillna(0)
twitter_agg_df = twitter_agg_df.resample('H').sum()

%store twitter_agg_df

# %%
from typing import Any, Dict

from pymongo import MongoClient
import pandas as pd

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.22.48.1:27017")
db = client["cs415_production"]
twitter_raw_coll_names = ["twitter_stream_counts"]

twitter_raw_count_dict = {}

for coll_name in twitter_raw_coll_names:
    result = list(db[coll_name].aggregate([
            {
                '$project': {
                    'created_at': {
                        '$dateTrunc': {
                            'date': '$created_at', 
                            'unit': 'minute', 
                            'binSize': 60, 
                            'timezone': 'America/New_York'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$created_at', 
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]))

    for entry in result:
        if entry["_id"] not in twitter_raw_count_dict:
            twitter_raw_count_dict[entry["_id"]] = 0
        twitter_raw_count_dict[entry["_id"]] += entry["count"]

twitter_raw_agg_df = pd.Series(twitter_raw_count_dict).fillna(0)
twitter_raw_agg_df = twitter_raw_agg_df.resample('H').sum()

%store twitter_raw_agg_df

# %%
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np

sns.set_theme(style="whitegrid")
sns.lineplot(reddit_agg_df, label="reddit (all sports)")
sns.lineplot(reddit_nfl_agg_df, label="reddit (nfl)")
sns.lineplot(twitter_agg_df, label="twitter (collected)")
sns.lineplot(twitter_raw_agg_df, label="twitter (raw)")
ax = sns.lineplot(odds_agg_df, label="odds api")
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
plt.tight_layout()

xmin, xmax = ax.get_xlim()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.set_xlabel("Date")
ax.set_ylabel("Document Updates (per hour)")
ax.set_title("Ingested Data Rate Over Time")
ax.set_xlim(xmin=xmin+3.5, xmax=xmax-1)
plt.show()


# %%
