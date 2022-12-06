from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import random
import seaborn as sns

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sns.set_theme(style="whitegrid")


def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    # CONNECTION_STRING = "mongodb+srv://user:pass@cluster.mongodb.net/myFirstDatabase"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient()

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['cs415_production']
#
# def data_plotter(data_frame, title ,group, fig):
#     axarr = fig.add_subplot(1, 1, 1)
#     df = data[[group, '_id']].rename(columns={"_id": "tweet_counts"}).groupby(group).count()
#     # print(df)
#     # print(df['lang'][:10])
#     counts = list(df.sort_values('tweet_counts', ascending=False)["tweet_counts"][:7])
#     # print(counts)
#     labels = ["English", "Japanese", "Spanish", "Portuguese", "Turkish", "French", "Arabic"]
#     ticks = range(len(counts))
#     plt.bar(ticks, counts, align='center', color='blue')
#     plt.xticks(ticks, labels)
#
#     plt.xticks(rotation=45, rotation_mode="anchor", ha="right")
#     plt.xlabel('languages', fontsize=11)
#     plt.ylabel('number of tweets', fontsize=11)
#     plt.tight_layout()
#     plt.title('NFL related tweets per language', fontsize=12)
#     plt.subplots_adjust(top=0.95)
#
#     return fig
#     # # plt.legend(loc="upper right")
#     # plt.show()





# def plot_signal(time, signal, title='', xlab='', ylab='',
#                 line_width=1, alpha=1, color='k',
#                 subplots=False, show_grid=True, fig=f):
#     # Skipping a lot of other complexity here
#
#     axarr = f.add_subplot(1, 1, 1)  # here is where you add the subplot to f
#     plt.plot(time, signal, linewidth=line_width,
#              alpha=alpha, color=color)
#     plt.set_xlim(min(time), max(time))
#     plt.set_xlabel(xlab)
#     plt.set_ylabel(ylab)
#     plt.grid(show_grid)
#     plt.title(title, size=16)
#
#     return (f)

# f = plot_signal(time, signal, fig=f)
def get_prob(num):
    if num > 0:
        return 100 / (num + 100)
    else:
        return (-1*num) / (-1*num + 100)

# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":

    db = get_database()
    dc = db['twitter_stream']
    df = pd.read_json('./data/odds_betting_with_outcomes_NEW.json')

    # odds_df = pd.read_json('./data/reddit_comments_timeseries_hourly_count_sentiment.json')
    # df.iloc[:, 0]["h2h_odds_fanduel"][0]['outcomes'][1]['price']
    for k in range(len(df.columns)):
        outputs = [[],[],[]]
        outputs2 = [[], [], []]
        outputs3 = [[], [], []]
        game = df.iloc[:, k]

        if (type(game["h2h_odds_fanduel"]) != list or type(game["h2h_odds_draftkings"]) != list or type(game["h2h_odds_barstool"]) != list):
            continue

        for i in range(len(game["h2h_odds_fanduel"])):
            outputs[0].append(pd.to_datetime(game["h2h_odds_fanduel"][i]['saved_at']))
            outputs[1].append(get_prob(game["h2h_odds_fanduel"][i]['outcomes'][0]['price']))
            outputs[2].append(get_prob(game["h2h_odds_fanduel"][i]['outcomes'][1]['price']))


        for i in range(len(game["h2h_odds_draftkings"])):
            outputs2[0].append(pd.to_datetime(game["h2h_odds_draftkings"][i]['saved_at']))
            outputs2[1].append(get_prob(game["h2h_odds_draftkings"][i]['outcomes'][0]['price']))
            outputs2[2].append(get_prob(game["h2h_odds_draftkings"][i]['outcomes'][1]['price']))

        for i in range(len(game["h2h_odds_barstool"])):
            outputs3[0].append(pd.to_datetime(game["h2h_odds_barstool"][i]['saved_at']))
            outputs3[1].append(get_prob(game["h2h_odds_barstool"][i]['outcomes'][0]['price']))
            outputs3[2].append(get_prob(game["h2h_odds_barstool"][i]['outcomes'][1]['price']))


        # df = ouputs
        plt.title('Fanduel, DraftKings (dotted) and Barstool (dashed) odds before game')

        data = pd.DataFrame(outputs).T[:-1]
        data2 = pd.DataFrame(outputs2).T[:-1]
        data3 = pd.DataFrame(outputs3).T[:-1]

        if game['winner'] == game['home_team']:
            ax = sns.lineplot(data=data, x=0, y=1, label=f'{game["home_team"]} (winner)', color='blue')
            ax = sns.lineplot(data=data, x=0, y=2, label=f'{game["away_team"]} (losers)', color='red')
            ax = sns.lineplot(data=data2, x=0, y=1, color='blue',alpha=0.5,linestyle="dotted")
            ax = sns.lineplot(data=data2, x=0, y=2, color='red',alpha=0.5,linestyle="dotted")
            ax = sns.lineplot(data=data3, x=0, y=1, color='blue',alpha=0.5,linestyle="dashed")
            ax = sns.lineplot(data=data3, x=0, y=2, color='red',alpha=0.5,linestyle="dashed")
        else:
            ax = sns.lineplot(data=data, x=0, y=2, label=f'{game["away_team"]} (winners)', color='blue')
            ax = sns.lineplot(data=data, x=0, y=1, label=f'{game["home_team"]} (losers)', color='red')
            ax = sns.lineplot(data=data2, x=0, y=2, color='blue',alpha=0.5,linestyle="dotted")
            ax = sns.lineplot(data=data2, x=0, y=1, color='red',alpha=0.5,linestyle="dotted")
            ax = sns.lineplot(data=data3, x=0, y=2, color='blue',alpha=0.5,linestyle="dashed")
            ax = sns.lineplot(data=data3, x=0, y=1, color='red',alpha=0.5,linestyle="dashed")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        plt.axvline(x=pd.to_datetime(game['commence_time']),linestyle="dashdot", color='blue')

        plt.xlabel('Time up to match', fontsize=11)
        plt.ylabel('Predicted probability of winning', fontsize=11)

        # custom_lines = [Line2D([0], [0], color='black', lw=2), ]
        # plt.plot(0, 0, linestyle='dotted', label='DraftKings', visible=False)
        #
        # custom_lines = [Line2D([0], [0], color='black', linestyle='dotted', lw=2)]

        plt.legend(loc="center left", borderaxespad=0)
        # plt.legend(custom_lines, ['DraftKings'])


        plt.tight_layout()
        plt.savefig(f"./data/plots/odds_up_to_game/game_{k}_{game['home_team'].rsplit(' ')[0]+'_'+game['home_team'].rsplit(' ')[1]}_{game['away_team'].rsplit(' ')[0]+'_'+game['away_team'].rsplit(' ')[1]}.png",
        bbox_inches="tight")
        plt.close()


    exit()


    df2 = pd.DataFrame(df["timeseries"][0])
    # plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)
    reddit_df2 = []
    # dc2 = db['twitter_stream_counts']
    # data = db['twitter_stream']
    # data = pd.DataFrame(list(dc.find({'context_annotations.domain.id': "28", 'lang': "en"})))
    odds = 700


    print(get_prob(odds))
    print((-1 * (-odds)) / (-1*(-odds) + 100))