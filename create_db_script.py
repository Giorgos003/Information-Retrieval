import random
import pandas as pd
from pathlib import Path
import unicodedata
import string
import sqlite3
import Preprocess_tools

# Opens the connection to the database
conn = sqlite3.connect("data.db")


script_dir = Path(__file__).resolve().parent

document_dir = script_dir / 'Greek_Parliament_Proceedings_1989_2020.csv'

reader = pd.read_csv(document_dir, chunksize=10000)

last_chunk = None
for i, df_chunk in enumerate(reader):

    df = df_chunk
    df.index.name = 'id'

    # filter unwanted columns
    df.drop(columns=["parliamentary_period", "parliamentary_session", "parliamentary_sitting"], inplace=True)

    # filter rows if the speeches are too small
    minimum_words = 10
    df = df[df['speech'].str.split().str.len() >= minimum_words]

    # filter rows if the names are non-existent
    df = df[df['member_name'].notna()]

    # creates a table named 'unfiltered_records' or appends in it
    # if already created and writes the chunk in the table
    df.to_sql('unfiltered_records', conn, if_exists='append')
    print(f"chunk {i} is written to the database")


    # For testing we leave that as a small number
    # which indicates how many batches are going
    # to be inserted in the database
    if i == 4:
        break

# Closes the connection to the databaase
conn.close()