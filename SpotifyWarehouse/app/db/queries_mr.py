import psycopg
import pandas as pd
import matplotlib.pyplot as plt
from setup import get_conn
from pathlib import Path

# Create functions with sql queries and then plotlib plot.
# manually or not move the output to flask outputs

# 0. Distribution of each measure
#     - Histograms of each measure for all songs
#     - Info about how skewed they are, etc.

# 4. Differnces in preferences among audiences
#     - Based on views, streams & likes determine which type (album, single, ...) is more popular on yt / spotify
#     - Which measures have higher value in songs more popular on yt & songs more popular on spotify
#     - Stacked bar chart -> or radar 


# 6. Official vs unofficial
#     - Are unofficial youtube tracks affecting original streams? (ratio?)
#     - grouped box plot -> 4 cases licensed, official video = (T, T), (T, F) ... -> show distribution of views / streams


# do singles differ in terms of spotify measures values from albums and compilations?
CURRENT_DIR = Path(__file__).parent.parent.resolve()
PLOTS_FOLDER = "flask/static/output"
PLOTS_DIR = CURRENT_DIR / PLOTS_FOLDER

def exec_query_singles_album_comp():
    with get_conn() as conn:
        query = """
        SELECT f.track,
        al.album_type,
                AVG(f.streams_spotify) as avg_streams
        FROM facts f
        JOIN album al ON f.album_id = al.album_id
        GROUP BY f.track, al.album_type
        ORDER BY avg_streams DESC
        LIMIT 10;
        """
        print("ee")
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=cols)
        
        fig, ax = plt.subplots(figsize=(12,6))
        ax.barh(df['track'], df['avg_streams'])
        plt.savefig(PLOTS_DIR / "plot.png")
        plt.show()
        print(df)

exec_query_singles_album_comp()