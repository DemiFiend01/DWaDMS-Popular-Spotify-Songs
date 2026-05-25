import psycopg
import flask

from setup import get_conn
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt

# TODO
# 1. (ok) Connect psycopg with database
# 2. (ok) Test queries
# 3. (ok) Init the DB
# 4. Clean the data
#    - (ok) Null values -> None found
#    - (ok) Normalize some of them
#    - (ok) Min & max for ranges?
# 5. (nope) Repeating values -> covers
#    - (nope) Make unique -> add column ['Title + artist'] -> append ' by {Artist}' at the end
# 6. (ok) Insert data into intermediate table?
# 7. Insert into the DB
#    * Zrobic wydupista tabele zamiast 'track' i 'spotify'
#    * Ranges
#      - (ok) Create range tables
#      - Fill range tables
#    * Fill the main wydupista_tabel
#

# 1. Write scripts for DW DB creation
#    - Range partitioning on streams / yt views
#    - Indexes on all analyzed measures
# 2. Run them with python (creation)
# 3. Load data from the staging area into 

BASE_DIR = Path(__file__).resolve().parent

scripts = BASE_DIR / "scripts"
datasets = BASE_DIR / "data"

def exec_sql(location : str | Path):
    ''' Executes a specific query from .sql file. '''
    with open(location, "r") as f:
        schema = f.read()

    if schema:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(schema)

def init_schema():
    ''' Inits the DB. If tables don't exist, they are created. '''
    exec_sql(scripts / "dw-schema.sql")
    exec_sql(scripts / "data-staging-area.sql")

def load_data_to_staging_area(src : str | Path):
    ''' Loads data from the .csv into the staging area - full_dataset table. '''

    # 0. Read data from .csv

    df = pd.read_csv(src)

    # 1. Construct the SQL query

    '''
    cols = ",".join(list(df.columns))
    with get_conn() as conn:
        with conn.cursor() as cur:
            with cur.copy(f"COPY full_dataset ({cols}) FROM STDIN") as copy:
                for row in df.itertuples():
                    copy.write_row(row)

        conn.commit()

    print(f"Loaded csv {src} into full_dataset table.")
    '''
    # Deprecated

    cols_num = len(df.columns)
    query = "INSERT INTO full_dataset "
    query += "(" + ",".join(list(df.columns))  + ") "
    query += "VALUES (" + "%s," * (cols_num - 1) + "%s)"

    with get_conn() as conn:
        with conn.cursor() as cur:
            for idx, row in df.iterrows():
                cur.execute(query, tuple(row.values))

        conn.commit()

def load_from_staging_area_to_dw(src : Path):
    
    pass

# Some info
def explore_dataset():

    df = pd.read_csv(datasets / "spotify-dataset.csv")

    print(f"Column types: {df.dtypes}")
    print(f"Shape: {df.shape}")
    print(f"Title & views: {df.loc[[0, 5], ['track', 'views_youtube']]}")
    print(f"Title - Views: {df.loc[0: 5, 'track': 'views_youtube']}")
    print(f"[5, 1]: {df.iloc[5, 1]}")
    print(f"Index: {df.index}")
    print(f"Columns: {df.columns}")
    print(f"Nulls: {df.isnull()}")
    print(f"Any nulls: {df[df.isnull()]}")
    print(f"Any artist null: {df['artist'].isnull()}")
    print(f"Artist that is null: {df[df['artist'].isnull()].index}")
    print(f"Views description: {df['views_youtube'].describe()}")
    print(f"Artist counts: {df['artist'].value_counts()}")

    print("All counts")

    # All counts:
    for col in df.columns:
        print(f"{col} :")
        print(f"{df[col].value_counts()}")

def clean_dataset(dest : str | Path, ranges_des : str | Path = None, normalize=False):
    '''
    Removes null values from spotify-dataset.csv & rows which have not information about some youtube statistics.
    Normalization of some metrics is optional.
    '''

    # 0. Read csv

    df = pd.read_csv(datasets / "spotify-dataset.csv")

    # 1. Null values removed

    # Null values: ['Channel'] & ['Title'] == 0
    not_on_yt = (df["channel"] == '0') | (df["title_youtube"] == '0') | (df['streams_spotify'] == 0)
    cleaned_df = df[~not_on_yt]

    if ranges_des:

        # 2. Find min / max for each range column

        range_cols = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_min", "views_youtube", "likes_youtube", "comments_youtube", "streams_spotify", "energyliveness"]
        ranges_df = df.loc[ : , range_cols]
        maxes = ranges_df.max()
        mins = ranges_df.min()

        min_maxes = list(zip(mins, maxes))
        ranges = dict(zip(range_cols, min_maxes))

        # Save ranges into separate df

        ranges_df = pd.DataFrame(ranges)
        ranges_df.to_csv(ranges_des, index=False)

    if normalize:
        # 3. Normalize the cleaned df
        clean_norm_df = (ranges_df - ranges_df.min()) / (ranges_df.max() - ranges_df.min())

        # 4. Replace cols in cleaned df with normalized ones
        for col in clean_norm_df.columns:
            new_col = col + "-norm"
            cleaned_df[new_col] = clean_norm_df[col]

    # 5. Save to 'spotify-dataset-clean.csv'
    cleaned_df.to_csv(dest, index=False)

# Tutorial
def dataset_messing():
    df = pd.read_csv(datasets / "spotify-dataset-clean.csv")

    _, row = next(df.iterrows())
    cols = [col.lower() for col in tuple(row.index)]
    vals = row.values
    print(cols)
    print(tuple(vals))

# Uncomment according to what you want to do

#explore_dataset()

#-1. Create a DB and connect to it with right configs
#    Actually do that manually
#    test_db - contains the tables without range tables
#    test_db_2 - contains tables with range tables (many of them actually)

# 0. Produces a 'spotify-dataset-clean.csv' in data/ directory
clean_dataset(dest = datasets / "spotify-dataset-clean.csv")

# 1. Creates the staging area and loads data from the clean .csv into it
exec_sql(scripts / "drop-data-staging-area.sql")
exec_sql(scripts / "data-staging-area.sql")
load_data_to_staging_area(datasets / "spotify-dataset-clean.csv")

# 2. Creates the actual DW schema & loads data into it from the staging area
exec_sql(scripts / "drop-dw-schema-new.sql")
exec_sql(scripts / "dw-schema-new.sql")
exec_sql(scripts / "load-from-staging-to-dw.sql")
