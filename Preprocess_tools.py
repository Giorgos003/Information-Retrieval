import random
import pandas as pd
from pathlib import Path
import unicodedata
import string

def remove_accents(text):
    # Normalize the string to NFD (Normalization Form Decomposed)
    normalized = unicodedata.normalize('NFD', text)

    # Remove the accents by keeping only non-mark characters (those that are not diacritical marks)
    return ''.join([char for char in normalized if not unicodedata.combining(char)])

def filter_dataframe(df):
    # filter unwanted columns
    df.drop(columns=["parliamentary_period", "parliamentary_session", "parliamentary_sitting"], inplace=True)

    # filter rows if the speeches are too small
    minimum_words = 10
    df = df[df['speech'].str.split().str.len() >= minimum_words]

    # filter rows if the names are non-existent
    df = df[df['member_name'].notna()]

    return df

def df_preprocess(df)->list:
    # Preprocessing every document (lowercase, tone and punctuation removal)
    docs = []
    allowed_punct = "/"

    for index, row in df.iterrows():
        whole_row = ' '.join(map(str, row.values))

        text = whole_row.lower()
        text = remove_accents(text)

        # This code removes unwanted characters
        # ######################################
        # text = ''.join(char if char not in string.punctuation or char == allowed_punct else " " for char in text)
        # # Replace some weird greek punctuations
        # text = text.replace("\u00AB", "").replace("\u00BB", "").replace("\u0384", "").replace("\u2019", "").replace("\u00BE","").replace("\u2215","")

        # This code specifies which caracters to keep
        # text = text.replace("/", "-")
        text = text.replace("\xba", "").replace("\xbb", "").replace("\xbc", "").replace("\xbd", "").replace("\xbe", "").replace("\u0456", "")
        text = ''.join(char if (char.isalnum() or char in string.ascii_lowercase + string.ascii_uppercase 
                                or char in 'αβγδεζηθικλμνξοπρστυφχψω'  # Greek lowercase letters
                                or char in 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'  # Greek uppercase letters
                                or char == allowed_punct) else " " 
                    for char in text)


        docs.append(text)

    return docs