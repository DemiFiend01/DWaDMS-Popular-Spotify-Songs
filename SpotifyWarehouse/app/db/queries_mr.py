import psycopg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from setup import get_conn
from pathlib import Path
from typing import List
from scipy.stats import skew

from queries_ml import create_df, gen_query_avg_stddev

# Create functions with sql queries and then plotlib plot.
# manually or not move the output to flask outputs

# 0. Distribution of each measure - DONE
#     - Histograms of each measure for all songs
#     - Info about how skewed they are, etc. 

# 6. Official vs unofficial
#     - Are unofficial youtube tracks affecting original streams? (ratio?) - DONE
#     - grouped box plot -> 4 cases licensed, official video = (T, T), (T, F) ... -> show distribution of views / streams - DONE

# do singles differ in terms of spotify measures values from albums and compilations?
CURRENT_DIR = Path(__file__).parent.parent.resolve()
PLOTS_FOLDER = "flask/static/output"
PLOTS_DIR = CURRENT_DIR / PLOTS_FOLDER

def query_avg_popularity_type_album(title=""):
    with get_conn() as conn:
        query = """
        SELECT al.album_type,
           AVG(f.streams_spotify) as avg_streams,
           AVG(f.views_youtube)   as avg_views,
           AVG(f.likes_youtube)   as avg_likes
        FROM facts f
        JOIN album al ON f.album_id = al.album_id
        GROUP BY al.album_type
        """
        df = create_df(query)

        x = np.arange(len(df['album_type']))
        width = 0.25

        # Normalization
        print(df)
        for col in ['avg_streams', 'avg_views', 'avg_likes']:
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

        print(df)
        
        fig, ax = plt.subplots(figsize=(10,6))

        ax.bar(x - width, df['avg_streams'], width, label='Spotify Streams')
        ax.bar(x,         df['avg_views'],   width, label='Youtube Views')
        ax.bar(x + width, df['avg_likes'],   width, label='Youtube Likes')

        ax.set_xticks(x, df['album_type'])
        ax.set_ylabel("Norm.avg.")
        ax.set_title("Popularity by diff. measures on Spotify and Youtube")
        ax.legend()

        plt.title("Norm. avg. streams, views and likes per album type.")
        plt.tight_layout()
        if title:
            plt.savefig(PLOTS_DIR / title)
        plt.show()

def query_avg_stddev_popularity_type_album(title=""):
    with get_conn() as conn:
        query = """
        SELECT al.album_type, """ + gen_query_avg_stddev(['streams_spotify', 'views_youtube', 'likes_youtube']) + """
        FROM facts f
        JOIN album al ON f.album_id = al.album_id
        GROUP BY al.album_type
        """
        df = create_df(query)

        x = np.arange(len(df['album_type']))
        width = 0.25

        # Normalization, both avg and sttdev
        print(df)
        pairs = {
            'avg_streams_spotify':  'stddev_streams_spotify',
            'avg_views_youtube':    'stddev_views_youtube',
            'avg_likes_youtube':    'stddev_likes_youtube',
        }

        for avg_col, std_col in pairs.items():
            min_val = df[avg_col].min()
            max_val = df[avg_col].max()
            df[std_col] = df[std_col] / (max_val - min_val)
            df[avg_col] = (df[avg_col] - min_val) / (max_val - min_val)

        print(df)
        
        fig, ax = plt.subplots(figsize=(10,6))

        ax.bar(x - width, df['avg_streams_spotify'], width, label='Spotify Streams', yerr=df['stddev_streams_spotify'], capsize=4)
        ax.bar(x,         df['avg_views_youtube'],   width, label='Youtube Views',   yerr=df['stddev_views_youtube'], capsize=4)
        ax.bar(x + width, df['avg_likes_youtube'],   width, label='Youtube Likes',   yerr=df['stddev_likes_youtube'], capsize=4)

        ax.set_xticks(x, df['album_type'])
        ax.set_ylabel("Norm.avg.")
        ax.set_title("Popularity by diff. measures on Spotify and Youtube")
        ax.legend()

        plt.title("Norm. avg. and st. dev. of streams, views and likes per album type.")
        plt.tight_layout()
        if title:
            plt.savefig(PLOTS_DIR / title)
        plt.show()

def histograms_of_each_measure(measures: List[str], title=""):
    with get_conn() as conn:
        for name in measures:
            query = """
            SELECT """ + name + """
            FROM facts f
            """
            df = create_df(query)
            skewness = skew(df[name])
            print(skewness)
            

            fig, ax = plt.subplots()
            ax.hist(df[name], bins=50) # 50 intervals
            ax.set_xlabel(f"{name} value")
            ax.set_ylabel("count")
            ax.set_title(f"Histogram of {name}")
            ax.legend()
            plt.title(f"Histogram of {name}\nSkewness: {float(skewness):.4f}")

            if title:
                plt.savefig(PLOTS_DIR / (title+f"{name}.png"))
            plt.show()

def youtube_official_streams_ratio(measures: List[str], title=""):
    with get_conn() as conn:
        query_official   = "SELECT " + ",".join(name for name in measures) + " FROM facts WHERE official_video = true"
        query_unofficial = "SELECT " + ",".join(name for name in measures) + " FROM facts WHERE official_video = false"

        df_official   = create_df(query_official)
        df_unofficial = create_df(query_unofficial)

        avg_official   = [
            (df_official["views_youtube"]  / df_official["streams_spotify"]).mean(),
            (df_official["likes_youtube"]  / df_official["streams_spotify"]).mean(),
            (df_official["comments"]       / df_official["streams_spotify"]).mean(),
        ]
        avg_unofficial = [
            (df_unofficial["views_youtube"] / df_unofficial["streams_spotify"]).mean(),
            (df_unofficial["likes_youtube"] / df_unofficial["streams_spotify"]).mean(),
            (df_unofficial["comments"]      / df_unofficial["streams_spotify"]).mean(),
        ]

        metrics = ['Youtube views / Spotify streams', 
                   'Youtube likes / Spotify streams', 
                   'Youtube comments / Spotify streams']
        x = np.arange(len(metrics))
        width = 0.35

        for i, (label, off, unoff) in enumerate(zip(metrics, avg_official, avg_unofficial)):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(['Official', 'Unofficial'], [off, unoff])
            ax.set_title(label)
            ax.set_ylabel("Metrics / Streams ratio")
            plt.tight_layout()
            if title:
                plt.savefig(PLOTS_DIR / (title + f"_{label.replace('/', '_')}.png"))
            plt.show()

def youtube_official_licensed_streams_ratio(measures: List[str], title=""):
    with get_conn() as conn:
        query_official_licensed   = "SELECT " + ",".join(name for name in measures) + " FROM facts WHERE official_video = true AND licensed = true"
        query_unofficial_licensed = "SELECT " + ",".join(name for name in measures) + " FROM facts WHERE official_video = false AND licensed = true"
        query_official_not_licensed = "SELECT " + ",".join(name for name in measures) + " FROM facts WHERE official_video = true AND licensed = false"
        query_unofficial_not_licensed = "SELECT " + ",".join(name for name in measures) + " FROM facts WHERE official_video = false AND licensed = false"
        df_official_licensed   = create_df(query_official_licensed)
        df_unofficial_licensed = create_df(query_unofficial_licensed)
        df_official_not_licensed   = create_df(query_official_not_licensed)
        df_unofficial_not_licensed = create_df(query_unofficial_not_licensed)

        groups = {
            'official+licensed':     df_official_licensed,
            'unofficial+licensed':   df_unofficial_licensed,
            'official+unlicensed':   df_official_not_licensed,
            'unofficial+unlicensed': df_unofficial_not_licensed,
        }

        metrics = {
            'views_youtube':  'Youtube views / Spotify streams',
            'likes_youtube':  'Youtube likes / Spotify streams',
            'comments':       'Youtube comments / Spotify streams',
        }

        for col, label in metrics.items():
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.boxplot([(df[col] / df['streams_spotify']) for df in groups.values()],
                       labels=groups.keys(), showfliers=False)
            ax.set_title(label)
            ax.set_ylabel("Metrics / Streams ratio")
            plt.tight_layout()
            if title:
                plt.savefig(PLOTS_DIR / (title + f"_{col}.png"))
            plt.show()

if __name__ == "__main__":
    #query_avg_popularity_type_album(title="avg_popularity_per_album_type.png")
    #query_avg_stddev_popularity_type_album(title="avg_and_sttdev_popularity_per_album_type.png")
    # histograms_of_each_measure(title="histograms_", measures=['danceability',
    #                                                         'energy',
    #                                                         'loudness',
    #                                                         'speechiness',
    #                                                         'acousticness',
    #                                                         'liveness',
    #                                                         'valence',
    #                                                         'tempo',
    #                                                         'instrumentalness'])
    # youtube_official_streams_ratio(title="youtube_spotify_streams_ratio", measures=['streams_spotify',
    #                                                                                  "views_youtube",
    #                                                                                  "likes_youtube",
    #                                                                                  "comments",
    #                                                                                  "official_video"],)
    youtube_official_licensed_streams_ratio(title="youtube_spotify_streams_licensed_ratio", measures=['streams_spotify',
                                                                                            "views_youtube",
                                                                                            "likes_youtube",
                                                                                            "comments",
                                                                                            "official_video"],)