#%%
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

import pandas as pd
from pymongo import MongoClient

with open("teamToEntitlementIds.json") as team_entitlement_json:
    team_entitlement_mappings = json.load(team_entitlement_json)


def convert_team_to_index(team_name: str) -> str:
    return team_name.lower().replace(" ", "-")


window_before = 2
window_after = 2
resample_rate = "90T"

reddit_lookup = {
    "buffalo-bills": "buffalobills",
    "miami-dolphins": "miamidolphins",
    "new-england-patriots": "Patriots",
    "new-york-jets": "nyjets",
    "baltimore-ravens": "ravens",
    "cincinnati-bengals": "bengals",
    "cleveland-browns": "Browns",
    "pittsburgh-steelers": "steelers",
    "houston-texans": "Texans",
    "indianapolis-colts": "Colts",
    "jacksonville-jaguars": "Jaguars",
    "tennessee-titans": "Tennesseetitans",
    "denver-broncos": "DenverBroncos",
    "kansas-city-chiefs": "KansasCityChiefs",
    "las-vegas-raiders": "oaklandraiders",
    "los-angeles-chargers": "Chargers",
    "dallas-cowboys": "cowboys",
    "new-york-giants": "NYGiants",
    "philadelphia-eagles": "eagles",
    "washington-commanders": "Commanders",
    "chicago-bears": "CHIBears",
    "detroit-lions": "detroitlions",
    "green-bay-packers": "GreenBayPackers",
    "minnesota-vikings": "minnesotavikings",
    "atlanta-falcons": "falcons",
    "carolina-panthers": "panthers",
    "new-orleans-saints": "Saints",
    "tampa-bay-buccaneers": "buccaneers",
    "arizona-cardinals": "AZCardinals",
    "los-angeles-rams": "LosAngelesRams",
    "san-francisco-49ers": "49ers",
    "seattle-seahawks": "Seahawks",
}

client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.27.80.1:27017")
db = client["cs415_production"]
games = list(
    db["nfl_games"].find(
        {"timestamp": {"$lt": datetime(2022, 11, 25, 12, 0, 0, tzinfo=timezone.utc)}}
    )
)

window_width = 1

for game in games:
    # Home Data
    home_team_entitlement_ids = team_entitlement_mappings.get(
        convert_team_to_index(game["home_team"]), []
    )

    print(
        f"home: looking for {reddit_lookup[convert_team_to_index(game['home_team'])]}"
    )
    print(
        f"away: looking for {reddit_lookup[convert_team_to_index(game['away_team'])]}"
    )

    home_tweets = list(
        db["twitter_stream"].find(
            {
                "context_annotations.entity.id": {"$in": home_team_entitlement_ids},
                "created_at": {
                    "$gte": game["timestamp"] - timedelta(days=window_before),
                    "$lt": game["timestamp"] + timedelta(days=window_after),
                },
            }
        )
    )

    home_tweet_df = pd.DataFrame(
        data={
            "polarity": [d["sentiment"]["polarity"] for d in home_tweets],
            "subjectivity": [d["sentiment"]["subjectivity"] for d in home_tweets],
        },
        index=[d["created_at"] for d in home_tweets],
    )

    if len(home_tweet_df) == 0:
        continue
    
    home_tweet_df = home_tweet_df.resample(resample_rate).mean().fillna(0)

    # ---

    home_reddit = list(
        db["reddit_stream_comments"].find(
            {
                "subreddit": reddit_lookup[convert_team_to_index(game["home_team"])],
                "created_at": {
                    "$gte": game["timestamp"] - timedelta(days=window_before),
                    "$lt": game["timestamp"] + timedelta(days=window_after),
                },
            }
        )
    )
    # TODO: remap it out of title_data and text_data
    # ) + list(
    #     db["reddit_stream_submissions"].find(
    #         {
    #             "subreddit": reddit_lookup[convert_team_to_index(game["home_team"])],
    #             "created_at": {
    #                 "$gte": game["timestamp"] - timedelta(days=7),
    #                 "$lt": game["timestamp"] + timedelta(days=window_after),
    #             },
    #         }
    #     )
    # )

    if len(home_reddit) == 0:
        continue

    home_reddit_df = pd.DataFrame(
        data={
            "polarity": [d["sentiment"]["polarity"] for d in home_reddit],
            "subjectivity": [d["sentiment"]["subjectivity"] for d in home_reddit],
        },
        index=[d["created_at"] for d in home_reddit],
    )
    print(home_reddit_df)
    home_reddit_df = home_reddit_df.resample(resample_rate).mean().fillna(0)

    # %store home_df

    # Away Data
    away_team_entitlement_ids = team_entitlement_mappings.get(
        convert_team_to_index(game["away_team"]), []
    )

    away_tweets = list(
        db["twitter_stream"].find(
            {
                "context_annotations.entity.id": {"$in": away_team_entitlement_ids},
                "created_at": {
                    "$gte": game["timestamp"] - timedelta(days=window_before),
                    "$lt": game["timestamp"] + timedelta(days=window_after),
                },
            }
        )
    )

    away_tweet_df = pd.DataFrame(
        data={
            "polarity": [d["sentiment"]["polarity"] for d in away_tweets],
            "subjectivity": [d["sentiment"]["subjectivity"] for d in away_tweets],
        },
        index=[d["created_at"] for d in away_tweets],
    )
    
    if len(away_tweet_df) == 0:
        continue

    away_tweet_df = away_tweet_df.resample(resample_rate).mean().fillna(0)

    # ---

    away_reddit = list(
        db["reddit_stream_comments"].find(
            {
                "subreddit": reddit_lookup[convert_team_to_index(game["away_team"])],
                "created_at": {
                    "$gte": game["timestamp"] - timedelta(days=window_before),
                    "$lt": game["timestamp"] + timedelta(days=window_after),
                },
            }
        )
    )
    # TODO: remap it out of title_data and text_data
    # ) + list(
    #     db["reddit_stream_submissions"].find(
    #         {
    #             "subreddit": reddit_lookup[convert_team_to_index(game["home_team"])],
    #             "created_at": {
    #                 "$gte": game["timestamp"] - timedelta(days=7),
    #                 "$lt": game["timestamp"] + timedelta(days=window_after),
    #             },
    #         }
    #     )
    # )
    #  + list(
    #     db["reddit_stream_submissions"].find(
    #         {
    #             "subreddit": reddit_lookup[convert_team_to_index(game["away_team"])],
    #             "created_at": {
    #                 "$gte": game["timestamp"] - timedelta(days=7),
    #                 "$lt": game["timestamp"] + timedelta(days=window_after),
    #             },
    #         }
    #     )
    # )

    if len(away_reddit) == 0:
        continue

    away_reddit_df = pd.DataFrame(
        data={
            "polarity": [d["sentiment"]["polarity"] for d in away_reddit],
            "subjectivity": [d["sentiment"]["subjectivity"] for d in away_reddit],
        },
        index=[d["created_at"] for d in away_reddit],
    )
    away_reddit_df = away_reddit_df.resample(resample_rate).mean().fillna(0)

    # %store away_df

    # sns.lineplot(
    #     away_tweet_df["polarity"],
    #     color="blue",
    #     linestyle=":",
    #     label=game["away_team"] + " : Twitter"
    #     # + (game["winner"] == game["away_team"] and " [WINNER]" or " [LOSER]"),
    # )
    # sns.lineplot(
    #     home_tweet_df["polarity"],
    #     color="red",
    #     linestyle=":",
    #     label=game["home_team"] + " : Twitter"
    #     # + (game["winner"] == game["home_team"] and " [WINNER] (" or " [LOSER]"),
    # )
    sns.lineplot(
        away_reddit_df["polarity"],
        color="blue",
        label=game["away_team"] + " : Reddit"
        # + (game["winner"] == game["away_team"] and " [WINNER]" or " [LOSER]"),
    )
    ax = sns.lineplot(
        home_reddit_df["polarity"],
        color="red",
        label=game["home_team"] + " : Reddit"
        # + (game["winner"] == game["home_team"] and " [WINNER] (" or " [LOSER]"),
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

    _, xmax = ax.get_xlim()

    ax.axvline(
        x=game["timestamp"],
        color=(game["winner"] == game["home_team"] and "red" or "blue"),
        linestyle="dashdot",
        label="Game Time",
        linewidth=2,
    )

    plt.tight_layout()

    ax.set_xlabel("Time")
    ax.set_ylabel("Polarity Score")
    ax.set_title(
        "Sentiment\n"
        + f"({game['home_score']}) {game['home_team']} vs {game['away_team']} ({game['away_score']})"
    )

    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)

    plt.savefig(
        f"sentiment/tighter-2day/reddit/{convert_team_to_index(game['home_team'])}_{convert_team_to_index(game['away_team'])}.png",
        bbox_inches="tight",
    )
    plt.show()
    plt.close()
# %%
