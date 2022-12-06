# %%
from datetime import datetime, timezone
from typing import Any, Dict

import pandas as pd
from pymongo import MongoClient

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.27.80.1:27017")
db = client["cs415_production"]

twitter_counts_count_dict = {}

result = list(
    db["twitter_stream_counts"].aggregate(
        [
            {
                "$project": {
                    "created_at": True
                }
            },
        ]
    )
)

for entry in result:
    if entry["created_at"] not in twitter_counts_count_dict:
        twitter_counts_count_dict[entry["created_at"]] = 0
    twitter_counts_count_dict[entry["created_at"]] += entry["count"]



twitter_counts_agg_df = pd.Series(twitter_counts_count_dict)
twitter_counts_agg_df = twitter_counts_agg_df.resample("D").sum()

%store twitter_counts_agg_df

#%%
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
ax = sns.histplot(twitter_counts_agg_df, binwidth=1)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
plt.tight_layout()

ax.set_xlabel("Date")
ax.set_ylabel("Tweets Per Day")
ax.set_title("Tweets Ingested (binned daily)")
plt.show()
# %%
