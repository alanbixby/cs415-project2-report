#%%
import json
from typing import Any, Dict

import pandas as pd
from pymongo import MongoClient

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.22.48.1:27017")
db = client["cs415_production"]
odds_coll_names = [
    col_name
    for col_name in db.list_collection_names()
    if col_name.startswith("odds_") and col_name != "odds_api_keys"
]

betting_types = ["h2h", "outrights", "spreads", "totals"]

games_dict = {}

for coll_name in odds_coll_names:
    cursor = db[coll_name].find({"sports_key": "americanfootball_nfl"})
    for doc in cursor:
        if doc["_id"] not in games_dict:
            winner = None
            home_score = None
            away_score = None
            try:
                game_outcome = db["nfl_games"].find_one({"_id": doc["_id"]})
                if game_outcome is not None:
                    home_score = game_outcome["home_score"]
                    away_score = game_outcome["away_score"]
                    winner = game_outcome["winner"]
            except:
                pass
            games_dict[doc["_id"]] = {
                "_id": doc["_id"],
                "home_team": doc["home_team"],
                "away_team": doc["away_team"],
                "commence_time": doc["commence_time"],
                "winner": winner,
                "home_score": home_score,
                "away_score": away_score,
            }

        if "h2h" in doc and len(doc["h2h"]) > 1:
            games_dict[doc["_id"]][f"h2h_{coll_name}"] = doc["h2h"]
        if "outrights" in doc and len(doc["outrights"]) > 1:
            games_dict[doc["_id"]][f"outrights_{coll_name}"] = doc["outrights"]
        if "spreads" in doc and len(doc["spreads"]) > 1:
            games_dict[doc["_id"]][f"spreads_{coll_name}"] = doc["spreads"]
        if "totals" in doc and len(doc["totals"]) > 1:
            games_dict[doc["_id"]][f"totals_{coll_name}"] = doc["totals"]
        print(games_dict[doc["_id"]])

# %store games_dict

with open(f"odds_betting_with_outcomes.json", "w") as outfile:
    outfile.write(json.dumps(games_dict, indent=2, default=str))

print("done")
