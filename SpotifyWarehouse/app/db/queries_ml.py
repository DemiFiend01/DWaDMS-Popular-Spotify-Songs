import psycopg
import pandas as pd
import matplotlib.pyplot as plt
from setup import get_conn
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Create functions with sql queries and then plotlib plot.
# manually or not move the output to flask outputs

# •	How do measure values correlate with instruments used in the song (acoustic vs electronic)
# TODO:
# - Read the analysis questions from report 1
# - Formulate other business questions
# - DB architecture, do we need timestamps?
# - Generate charts for each questions

# Fact: 
# - track
# Measures:
# - artist
# - album
# - youtube_channel

# Questions:
'''
My Questions:

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

1. (ok) Biggest hits vs least popular songs
    - Compare average metrics between least popular (<1M) & most popular (>1B) tracks.
    - Radar chart / Parallel coordinates plot
2. Acoustic vs Electronic
    - Difference between measures for songs with low and high acousticness
    - Grouped Bar chart with error bars
3. Audio feature binning
    - Which value / range of each metric (especially tempo, loudness, danceability) have the highest number of views / streams
    - Grid of bar charts / Heatmap

## Spotify vs Youtube

4. Differnces in preferences among audiences
    - Based on views, streams & likes determine which type (album, single, ...) is more popular on yt / spotify
    - Which measures have higher value in songs more popular on yt & songs more popular on spotify
    - Stacked bar chart

5. Do youtube views influence spotify streams
    - Based on ratio likes, comments / views tracks have higher number of streams on spotify than tracks with lower ratios?
    - Scatter plot + trendline

6. Official vs unofficial
    - Are unofficial youtube tracks affecting original streams? (ratio?)
    - grouped box plot -> 4 cases licensed, official video = (T, T), (T, F) ... -> show distribution of views / streams

* High level perspective

7. Biggest producers vs smallest
    - Is the distribution of views flat or rather skewed, so that a small number of artists generates most of the views?
    - Histogram / Pareto chart

8. Radio Optimization
    - Are songs that are produced for radio more successfull in terms of views / streams?
    - What is optimal length of the song that maximizes the views / streams?
    - Area chart / Dual-Axis Line Chart

9. Sonic variety across albums
    - Mean & std dev for each album for each measure. Is there difference between singles, compilations, etc.
    - Box / Whisker Plot

'''

BG_WHITE = "#fbf9f4"
BLUE = "#2a475e"
GREY70 = "#b3b3b3"
GREY_LIGHT = "#f2efe8"
COLORS = ["#FF5A5F", "#FFB400", "#007A87"]

DUMMY = ["Meow", "Hau", "Ihiahia"]

# TODO: Add bar plots for means of loudness & tempo
def biggest_vs_smallest_tracks():
    '''
    Creates a radar plot which compares average values of normalized spotify metrics 
    of the most popular with the least popular tracks.
    '''
    # 0. Query DB
    #    - Spotify Metrics without: loudness, temp <- not normalized
    #    - streams > 1B
    #    - streams < 1M

    MIN_STREAMS = 10 ** 6
    MAX_STREAMS = 10 ** 9

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT " \
            "danceability," \
            "energy," \
            "speechiness," \
            "acousticness," \
            "liveness," \
            "valence," \
            "instrumentalness" \
            " FROM facts WHERE streams_spotify < (%s)",
                        (MIN_STREAMS,))
            low_streams = []
            cols = [col[0] for col in cur.description]
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                low_streams.append(row)
                
            df_low = pd.DataFrame(low_streams, columns=cols)

            cur.execute("SELECT "\
            "danceability," \
            "energy," \
            "speechiness," \
            "acousticness," \
            "liveness," \
            "valence," \
            "instrumentalness" \
            " FROM facts WHERE streams_spotify > (%s)",
                        (MAX_STREAMS,))
            high_streams = []
            cols = [col[0] for col in cur.description]
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                high_streams.append(row)
            
            df_high = pd.DataFrame(high_streams, columns=cols)

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

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1.0]
            )
        ),
        showlegend=True
    )

    fig.show()

def acoustic_vs_electronic():

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



