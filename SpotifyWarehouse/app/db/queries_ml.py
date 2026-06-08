import pandas as pd
import matplotlib.pyplot as plt
from setup import get_conn
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from decimal import Decimal
from pathlib import Path

from typing import List, Tuple

# Tutorials:
# https://plotly.com/python/radar-chart/

# Create functions with sql queries and then plotlib plot.
# manually or not move the output to flask outputs

# How do measure values correlate with instruments used in the song (acoustic vs electronic)
# TODO:
# - Add descriptions & title
# - (ok) Save to file

# Fact: 
# - track
# Measures:
# - artist
# - album
# - youtube_channel

'''
My Question:

I need to think what business questions I can answer with this data. We decided not to load this into OLAP cube, instead we'll be querying the DB with sql. 
So what I though about:
1. Average value with mean and standard deviation of each spotify measure with regard to whether track was acoustic or not (acoustincesss < 0.5 or not).
This could be visualized on bar charts with standard deviation as error uh arms / bars.

2. Similiar analysis but this time the average number of streams & views on youtube with regard to each measure. These would be bar plots for ranges. For example average number of streams for songs that have acoustincess values oin between 0.2 and 0.4, 0.4 and 0.6, ..., and so on for each measure. 
We would need some pretty way to push all of this into a single plot for measures that are normalized.

3. Some basic statistical analysis, like histograms for each measure, mean, mode, median and standard deviation. Just for the sake of having those. 
4. Distribution of songs with regard to youtube views and number of streams on spotify for each specific artist. I am unsure what that would actually mean. We could evaluate the difference for each song between the number of streams on spotify and views on youtube and then plot those differences for selected channel or album. Or for all albums from a single channel on one chart?

Eh, I'm just sort of throwing ideas into the void.
Business questions again.
What an artist may ask themselves.

A. Do my viewers enjoy acoustic songs more or digital?
B. Which measure correleates the most with number of views / streams?
C. Is there a significant difference between number of streams and views on youtube for my songs? If so, why should I keep posting on spotify?
D. What are average values of measures from each album?
E. Are the non-licensed songs on youtube that are mine are having more views than my original songs on spotify?

Eh, that much for an artist I would say.
So now what could a company like spotify ask themselves if they had a datawarehouse like this?

A'. Which measures for all artists correlate the most with higher spotify streams
B'. Which measures correlate with higher youtube views.
C'. Histogram of artists spotify streams (how many artists in each range)

'''

'''
Gemini proposition:

## Hit mechanics, what is popular?

0. Distribution of each measure
    - Histograms of each measure for all songs
    - Info about how skewed they are, etc.

1. (ok) Biggest hits vs least popular songs
    - Compare average metrics between least popular (<1M) & most popular (>1B) tracks.
    - Radar chart / Parallel coordinates plot

2. (ok) Acoustic vs Electronic
    - Difference between measures for songs with low and high acousticness
    - Grouped Bar chart with error bars

2.5 (ok) Measures avg & std dev below & above treshold
    - Generate bar charts of all other measures beside the one that has set threshold

3. (almost - wrong order of columns) Audio feature binning
    - Which value / range of each metric (especially tempo, loudness, danceability) have the highest number of views / streams
    - Purpose is to establish a desireable range of each metric which maximizes the streams number.
    - Grid of bar charts / Heatmap

## Spotify vs Youtube

4. Differnces in preferences among audiences
    - Based on views, streams & likes determine which type (album, single, ...) is more popular on yt / spotify
    - Which measures have higher value in songs more popular on yt & songs more popular on spotify
    - Stacked bar chart -> or radar 

4.5 YouTube & Spotify comparison
    - Is it redundant with 2. ?
    - General comparison of measures and other features

5. (ok - without comments/views ratio) Do youtube views influence spotify streams
    - Based on ratio likes, comments / views tracks have higher number of streams on spotify than tracks with lower ratios?
    - Scatter plot + trendline

6. Official vs unofficial
    - Are unofficial youtube tracks affecting original streams? (ratio?)
    - grouped box plot -> 4 cases licensed, official video = (T, T), (T, F) ... -> show distribution of views / streams

## High level perspective

7. (ok) Biggest producers vs smallest
    - Is the distribution of views flat or rather skewed, so that a small number of artists generates most of the views?
    - Histogram / Pareto chart

8. (ok) Radio Optimization
    - Are songs that are produced for radio more successfull in terms of views / streams?
    - What is optimal length of the song that maximizes the views / streams?
    - Area chart / Dual-Axis Line Chart

9. Sonic variety across albums
    - Mean & std dev for each album for each measure. Is there difference between singles, compilations, etc.
    - Box / Whisker Plot

- Add descriptions to all plots
- Save plots into files. 

'''

# Otherwise Flask will just have issues and will create more urls
CURRENT_DIR = Path(__file__).parent.parent.resolve()
PLOTS_FOLDER = "flask/static/output"
PLOTS_DIR = CURRENT_DIR / PLOTS_FOLDER
print(f"The pictures will be saved in: {PLOTS_DIR}")

Path.mkdir(PLOTS_DIR, parents=False, exist_ok=True)

# ------ Helper function ------ #

def gen_query_avg_stddev(measures : List[str]):
        '''
        Generates a list of columns for SQL query in the following format: 
        avg(name) as avg_name, stddev_pop(name) stddev_name. name is taken from the measures list.

        Args:
            measures (list) : Names of table columns to include in the query.
        '''
        return ", ".join([f"avg({name}) as avg_{name}, stddev_pop({name}) stddev_{name} " for name in measures])

def create_df(query : str) -> pd.DataFrame | None:
    ''' Executes SQL query and returns a pandas dataframe based on the fetched data or None if no query is given. '''

    if not query:
        return None

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                cols = [col[0] for col in cur.description]
                return pd.DataFrame(rows, columns=cols)
    except Exception as e:
        print(f"EXCEPTION in create_df(): {e}")
        return None

# ------ Plots ------ #

# TODO: Add bar plots for means of loudness & tempo
def biggest_vs_smallest_tracks(measures : List[str], unpopular : int = 10 ** 6, popular : int = 10 ** 9, title=""):
    '''
    Creates a radar plot which compares average values of normalized spotify metrics between most popular and least popular tracks.
    Args:
        measures  (list) : List of measures to analyze.
        unpopular (int)  : Max number of streams a track may have to be considered unpopular.
        popluar   (int)  : Min number of streams a track may have to be considered popular.
    '''
    # 0. Query DB

    query_cols = ", ".join(measures)
    query_low = "SELECT " + query_cols + f" FROM facts WHERE streams_spotify < {unpopular}"
    query_high = "SELECT " + query_cols + f" FROM facts WHERE streams_spotify > {popular}"

    df_low = create_df(query_low)
    df_high = create_df(query_high)

    # 1. Calculate avg values for each metric

    means_low = df_low.mean()
    means_high = df_high.mean()

    # 2. Radar chart

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=means_low.to_list(),
        theta=means_low.index,
        fill="toself",
        name="Unpopular Tracks"
    ))

    fig.add_trace(go.Scatterpolar(
        r=means_high.to_list(),
        theta=means_high.index,
        fill="toself",
        name="Popular Tracks"
    ))

    fig.add_annotation()

    fig.add_annotation(dict(
        text=f"Comparison of evarage values of different measures between popular and unpopular songs.\n" \
        f"Song is popular if streams_spotify > {popular}\n" \
        f"Song is unpopular if streams_spotify < {unpopular}",
        xref="paper", yref="paper",
        x=0, y=-0.2,
        showarrow=False,
        align="left"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1.0]
            )
        ),
        showlegend=True
    )

    if title:
        fig.write_image(PLOTS_DIR / (title + ".png"))

    fig.show()

def avg_dev_for_measure_range(measure : str, boundry : float, names : Tuple[str, str], data : List[str]=[], title=""):
    ''' 
    Produces a grouped bar plot of avg values of all measures for tracks that are categorized into 2 groups,
    based on the value of chosen measure.
    Args:
        measure  (str)   : Measure name which will be used to split data.
        boundary (float) : Value which will partition the table.
        names    (tuple) : Names of the upper and lower category.
        data     (list)  : Names of measurs to take into account (avg + stddev).
    '''

    ''' Produces a grouped bar plot, showing mean values of measures for tracks with acousticness > or < than 0.5.'''

    # 0. SQL 
    #    - Group songs with acoustincess < 0.5 and > 0.5
    #    - Name the groups acoustic / digital
    #    - calculate avg & std dev for each

    query = ""\
            "select status, " + gen_query_avg_stddev(data) + " from( "\
            "select " + ", ".join(data) + ", "\
            "case "\
                "when acousticness < 0.5 then 'acoustic' "\
                "when acousticness >= 0.5 then 'digital' "\
                "else'unknown' "\
                "end as status "\
            "from facts) "\
            "group by status;"

    df =  create_df(query)
    print(df)
    # 1. Bar plot
    #    - Red for lower, green for upper bound
    
    # Preapre plot data
    y_1 = df.iloc[0].tolist()[1 : : 2]
    y_2 = df.iloc[1].tolist()[1 : : 2]
    x = np.arange(len(y_1))
    stddev_1 = df.iloc[0].tolist()[2 : : 2]
    stddev_2 = df.iloc[1].tolist()[2 : : 2]

    width = 0.25

    fig, ax = plt.subplots(figsize=(10,10))    

    # Add bars to the plot 
    bars_1 = ax.bar(x - width / 2, y_1, width, label="acoustic", color="Red")
    error_bars_1 = ax.errorbar(x - width / 2, y_1, stddev_1, fmt="none", capsize=2, color="black")
    bars_2 = ax.bar(x + width / 2, y_2, width, label="digital", color="Blue")
    error_bars_2 = ax.errorbar(x + width / 2, y_2, stddev_2, fmt="None", capsize=2, color="black")

    ax.set_ylim(top=1.0, bottom=0.0)

    # Set label to each bar 
    ax.set_xticks(x, df.columns[1 : : 2])

    ax.set_xlabel("Measures")
    ax.set_ylabel("avg +\- stddev")
    ax.legend()

    plt.tight_layout()
    
    plt.title("Average measures value in popular and unpopular songs")
    #fig.suptitle("Average measures value in popular and unpopular songs.")
    plt.figtext(x=0.5, y=-0.02, ha="center", wrap=True, s=f"Tracks are split into 2 groups, based on {measure} value. The boundary has value: {boundry}." \
                f"Average values of all measures for both groups of tracks are displayed with standard deviatio nas error bars.")

    if title:
        plt.savefig(PLOTS_DIR / title, bbox_inches="tight")

    plt.show()

def audio_feature_binning(all_measures : List[List[str]], n : int, title=""):
    ''' 
    Draws a grid of bar charts for each selected measure.
    Single bar chart splits the tracks into n buckets based on measure values and counts the avg of spotify streams for that range.
    Args:
        all_measures (list(list)) : Matrix of measures to analyze.
        n            (int)        : Number of buckets.
    '''
    
    def query_select_avg_for_measure_range(measure : str, n : int):
        '''
        Creates query for the audio_feature_binning() function.
        Query splits tracks into n buckets between min and max value of the measure.
        '''
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT max({measure}), min({measure}) FROM facts")
                rows = cur.fetchone()
                m_min = float(rows["min"]) 
                m_max = float(rows["max"]) 

                range_vals = np.ones(n + 1) * m_min + np.arange(n + 1) * ((m_max-m_min) / n)
                print(range_vals)

                #range_vals = np.arange(m_min, m_max, (m_max-m_min) / n)

                whens = []
                for i in range(n):
                    # Format to 2 decimal places as a string so the SQL is clean
                    low = "{:.2f}".format(range_vals[i])
                    high = "{:.2f}".format(range_vals[i+1])
                    whens.append(f"WHEN {measure} BETWEEN {low} AND {high} THEN '{low}-{high}'")

                

                # Construct the query
                return  "SELECT " \
                        "CASE " + "\n".join(whens) + "\nELSE 'other' " \
                        "END AS bucket, " \
                        "AVG(streams_spotify) " \
                        "FROM facts " \
                        "GROUP BY bucket; "

    # 0. Dimensions of the plot

    dim_x = len(all_measures[0])
    dim_y = len(all_measures)
    fig = plt.figure(figsize=(10,10))

    i = 0
    for lm in all_measures:
        j = 0
        for measure in lm:
            # 1. Fetch data
                    
            query = query_select_avg_for_measure_range(measure, 5)
            df = create_df(query)
            df = df.sort_values(by="bucket", ascending=True)
            print(df)

            # 2. Prepare plot data

            dft = df.T
            ax = fig.add_subplot(dim_y, dim_x, i * dim_x + j + 1)

            x = np.arange(len(dft.iloc[0]))
            y = dft.iloc[1].tolist() 

            width = 0.25

            # 3. Setup plot

            bars = ax.bar(x=x, height=y, width=width, label="acousticness", color="red")
            ax.set_xticks(ticks=x, labels=dft.iloc[0].values, fontsize="small", rotation=30)

            ax.set_xlabel(f"range of {measure}", fontsize="small")
            ax.set_ylabel("avg(streams_spotify)", fontsize="small")

            plt.xticks(fontsize="small")
            plt.yticks(fontsize="small")
            
            j += 1
        i += 1

    plt.tight_layout()
    plt.suptitle(x=0.5, y=1.0, t="Average streams for different song types")
    plt.subplots_adjust(bottom=0.2)
    plt.figtext(x=0.5, y=0.05, ha="center", wrap=True, 
                s="Songs are bucketized for different measure ranges. For each range, the average number of spotify streams is calculated.")

    if title:
        plt.savefig(PLOTS_DIR / title)
    plt.show()

# Based on ratio likes, comments / views tracks have higher number of streams on spotify than tracks with lower ratios?
# TODO:
# - Fix the color map
# - Include the analysis of comments and likes
def youtube_influences_spotify(title="", max_views_youtube=10**10, max_spotify_streams=10**10):
    ''' 
    Draws a trendline & calculates the coefficients for dependency between spotify streams & youtube views (if there is any?).
    '''

    # 0. Query

    query = "select views_youtube, streams_spotify, likes_youtube, comments from facts;"

    # 1. Extract data from DB

    df = create_df(query)

    # 2. Preapre data & linear regression

    x = df["views_youtube"].tolist()
    y = df["streams_spotify"].tolist()

    likes_views_ratio = df["likes_youtube"].to_numpy() / df["views_youtube"].to_numpy()
    likes_views_ratio = np.linalg.norm(likes_views_ratio)

    a, b = np.polyfit(x, y, deg=1)
    a = round(a, 2)
    b = round(b, 2)
    xseq = np.linspace(0, max_views_youtube, num=2)

    color_map = plt.cm.cool(likes_views_ratio, ) #load_cmap("cool")

    # 3. Scatter plot with a trend line
    plt.figure(figsize=(10,10))

    plt.scatter(x=x, y=y, s=0.1, edgecolors=color_map)
    plt.plot(xseq, a * xseq + b, color="red")

    plt.xlabel("views_youtube")
    plt.ylabel("streams_spotify")

    plt.xlim(left=0, right=max_views_youtube)
    plt.ylim(bottom=0, top=max_spotify_streams)

    ax = plt.gca()
    ax.annotate(f"y = a * views_youtube + b\na = {np.format_float_scientific(a, 2)}\nb = {np.format_float_scientific(b, 2)}", xy=(0.95,0.95), xycoords='axes fraction', ha='right', va='top')

    plt.legend()

    plt.tight_layout()
    plt.suptitle(x=0.5, y=1.0, t="Streams vs Views")
    plt.subplots_adjust(bottom=0.2)
    plt.figtext(x=0.5, y=0.1, ha="center", wrap=True,
                s="Trendline showing correlation between the number of streams on spotify and views on youtube.")

    if title:
        plt.savefig(PLOTS_DIR / title)

    plt.show()

# UNFINISHED
def official_vs_unoffical():
    pass
    # TODO:
    # 1. Think again what we want to analyze in here
    # 2. Read more about boxplots

    # Box plots seem to be good at showing distribution over time (or over change of some variable)
    # 2 separate plots

def big_vs_small_producers(title=""):
    '''
    Splits artists into buckets based on the total number of streams they generated 
    and then counts, how many artsits fall into specific range of generated streams.
    Draws a histogram.
    '''

    # 0. Query

    # Already creates histogram data (buckets and counts) with sql. Use bar chart to visualize
    # Deprecated as matplotlib uses numpy which does that by default
    '''
    query = "with artist_sums as ( " \
            "select artist_id, sum(streams_spotify) as streams_total " \
            "from facts " \
            "group by 1 " \
            "order by 2 desc ) " \
            "select floor(streams_total / cast(power(10, 8) as float8)) * cast(power(10, 8) as bigint) as streams_bucket, " \
            "count(artist_id) as artist_count " \
            "from artist_sums " \
            "group by 1 " \
            "order by 1; "
    '''
    
    query = "select artist_id, sum(streams_spotify) as streams_total " \
            "from facts " \
            "group by 1 " \
            "order by 2 desc;"

    # 1. Create df

    df =create_df(query)

    # 2. Plot histogram

    x = df['streams_total']
    bins = 100

    plt.figure(figsize=(10,10))
    plt.hist(x=x, bins=bins)

    plt.xlabel("Streams range")
    plt.ylabel("Artists count")

    plt.tight_layout()
    plt.suptitle(t="Artists count")
    plt.subplots_adjust(bottom=0.2)
    plt.figtext(x=0.5, y=0.05, ha="center", wrap=True,
                s="Histogram which counts how many artists generate streams from given range.")

    if title:
        plt.savefig(PLOTS_DIR / title)

    plt.show()

# TODO:
# - Zoom in on the denser part of graph or at the the ranges aroud 3 maxes
def optimal_track_length(title=""):
    ''' 
    Creates area chart with avg spotify streams on the y-axis and track duration in seconds on x-axis.
    '''

    query = "select round(cast(duration_min as numeric), 2) as duration, avg(streams_spotify) as avg_streams " \
            "from facts " \
            "group by 1 " \
            "order by 1 asc; "
    
    df = create_df(query)

    x = df["duration"].to_numpy() * Decimal(60.0) # Convert to seconds
    y = df["avg_streams"].tolist()

    fig, ax = plt.subplots(figsize=(10,10))

    ax.fill_between(x, y)

    ax.set_xlabel("duration [s]")
    ax.set_ylabel("avg(streams)")

    plt.tight_layout()
    plt.suptitle(x=0.5, y=1.0, t="Optimal track length")
    plt.subplots_adjust(bottom=0.2)
    plt.figtext(x=0.5, y=0.05, ha="center", wrap=True,
                s="Area chart of the average number of streams per tracks duration in seconds.")

    if title:
        plt.savefig(PLOTS_DIR / title)

    plt.show()

# Use it to compare average values of different measures for different kinds of albums.
# Measures values must be all on a single scale.
def albums_variety(measures : List[str], title=""):
    ''' 
    Plots a bar chart of average values of specified spotify measures for all different kinds of albums. 
    
    Args:
        measures (list) : Names of the measures to analyze.
    '''
    # 0. Generate query

    query_cols = gen_query_avg_stddev(measures)
    query = "select a.album_type, " + query_cols + " from facts as f join album as a " \
            "on f.album_id=a.album_id " \
            "group by 1; "

    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1. Read DB
            cur.execute(query)
            rows = cur.fetchall()
            cols = [col[0] for col in cur.description]

            df = pd.DataFrame(rows, columns=cols)

            # 2. Preapre data for bar plot

            labels = df.columns[ 1 : : 2] # Names of each metric for which avg has been calculated
            
            keys = df['album_type'].tolist()
            values = df.iloc[ : , 1 : : 2].to_numpy() # Average value of each metric
            errors = df.iloc[ : , 2 : : 2].to_numpy() # stddev for each metric

            heights = dict(zip(keys, values))
            error_heights = dict(zip(keys, errors))
            x = np.arange(len(labels))
            
            width = 0.25

            # 3. Plot the bar plot

            fig, ax = plt.subplots(figsize=(10,10))

            multip = 0
            for label, avg in heights.items():
                offset = width * multip
                yerr = error_heights[label]

                b = ax.bar(x + offset, avg, 0.25, label=label, yerr=yerr)
                multip += 1

            ax.set_xticks(x + width, labels, rotation=30)
            ax.set_ylim(0.0, None)

            ax.legend()

            plt.tight_layout()
            plt.suptitle(t="Average measure in different albums")
            plt.subplots_adjust(bottom=0.2)
            plt.figtext(x=0.5, y=0.0, ha="center", wrap=True,
                        s=f"Average values of measures: {', '.join(measures)} for different kinds of albums.")

            if title:
                plt.savefig(PLOTS_DIR / title)

            plt.show()

# DUMMY
def correlation_measure_value_instrument_type():
    ''' Creates diagrams which list in pairs measure values for songs which use acoustic instruments & songs which use electronic instruments. '''

    with get_conn() as conn:
        # 0. Download data

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM facts")
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=cols)

            # 1. Count average values for each measure over all tracks, for each instrument type

            df['instrument_type'] = np.where(df['acousticness'] >= 0.5, 'acoustic', 'electronic')
                
            measures = ['danceability', 'energy', 'loudness', 'speechiness', 'liveness', 'valence', 'tempo', 'instrumentalness']
            avg_measures = df.groupby('instrument_type')[measures].mean().reset_index()
            print(avg_measures)

if __name__ == "__main__":
    biggest_vs_smallest_tracks(['danceability', 'energy', 'speechiness', 'acousticness', 'liveness', 'valence', 'instrumentalness'], title="biggest_vs_smallest_tracks")
    avg_dev_for_measure_range('acousticness', 0.5, ('acoustic', 'digital'), ["danceability", "energy", "speechiness", "liveness", "valence", "instrumentalness"], "avg_dev_for_measure_range")
    audio_feature_binning([["acousticness", "liveness"], ["speechiness", "tempo"]], 5, title="audio_feature_binning")
    youtube_influences_spotify(title="youtube_influences_spotify_full", max_views_youtube=10**10, max_spotify_streams=10**10)
    youtube_influences_spotify(title="youtube_influences_spotify_dense", max_views_youtube=10**9, max_spotify_streams=10**9)
    big_vs_small_producers(title="big_vs_small_producers")
    optimal_track_length(title="optimal_track_length")
    albums_variety(['danceability', 'energy', 'speechiness', 'acousticness', 'liveness', 'valence', 'instrumentalness'], title="albums_variety")





