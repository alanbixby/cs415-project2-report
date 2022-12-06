# %%
from datetime import datetime, timezone
from typing import Any, Dict

import pandas as pd
from pymongo import MongoClient

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.22.48.1:27017")
db = client["cs415_production"]

reddit_politics_count_dict = {}

result = list(
    db["reddit_stream_submissions"].aggregate(
        [
            {
                "$match": {
                    "subreddit": "politics",
                    "created_at": {
                        "$gte": datetime(2022, 11, 1, 4, 0, 0, tzinfo=timezone.utc),
                        "$lt": datetime(2022, 11, 15, 5, 0, 0, tzinfo=timezone.utc),
                    },
                }
            },
            {
                "$project": {
                    "created_at": {
                        "$dateTrunc": {"date": "$created_at", "unit": "hour"}
                    }
                }
            },
            {"$group": {"_id": "$created_at", "count": {"$sum": 1}}},
        ]
    )
)

for entry in result:
    if entry["_id"] not in reddit_politics_count_dict:
        reddit_politics_count_dict[entry["_id"]] = 0
    reddit_politics_count_dict[entry["_id"]] += entry["count"]

reddit_politics_agg_df = pd.Series(reddit_politics_count_dict)
reddit_politics_agg_df = reddit_politics_agg_df.resample("H").sum()

%store reddit_politics_agg_df

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

#%%
import seaborn as sns

sns.set_theme(style="whitegrid")
ax = sns.lineplot(reddit_politics_agg_df)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
plt.tight_layout()

xmin, xmax = ax.get_xlim()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax.set_xlabel("Date")
ax.set_ylabel("Submissions Per Hour")
ax.set_title("/r/politics Submissions (binned hourly)")
ax.set_xlim(xmin=xmin + 3.5, xmax=xmax - 1)
plt.show()
# %%
