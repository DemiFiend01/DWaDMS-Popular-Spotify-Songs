import psycopg
import pandas as pd
import matplotlib.pyplot as plt
from setup import get_conn

# Create functions with sql queries and then plotlib plot.
# manually or not move the output to flask outputs

# do singles differ in terms of spotify measures values from albums and compilations?

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

        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=cols)
        
        fig, ax = plt.subplots(figsize=(12,6))
        ax.barh(df['track'], df['streams_spotify'])
        plt.savefig("plot.png")
        plt.show()
        print(df)