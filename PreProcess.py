import pandas as pd
from pathlib import Path
import unicodedata
import string

# Reading the csv and filtering some rows and columns
# -------------------------------------------------------

script_dir = Path(__file__).resolve().parent

document_dir = script_dir / 'Greek_Parliament_Proceedings_1989_2020_DataSample.csv'

df = pd.read_csv(document_dir)

# filter unwanted columns
df.drop(columns=["parliamentary_period", "parliamentary_session", "parliamentary_sitting"], inplace=True)

# filter rows if the speeches are too small
minimum_words = 10
df = df[df['speech'].str.split().str.len() >= minimum_words]

# filter rows if the names are non-existent
df = df[df['member_name'].notna()]


# Transform pandas dataframe into a list and preprocess
# every record of that dataframe
# -------------------------------------------------------

def remove_accents(text):
    # Normalize the string to NFD (Normalization Form Decomposed)
    normalized = unicodedata.normalize('NFD', text)

    # Remove the accents by keeping only non-mark characters (those that are not diacritical marks)
    return ''.join([char for char in normalized if not unicodedata.combining(char)])


# Preprocessing every document (lowercase, tone and punctuation removal)
docs = []
allowed_punct = '/'

for index, row in df.iterrows():
    whole_row = ' '.join(map(str, row.values))

    text = whole_row.lower()
    text = remove_accents(text)
    text = ''.join(char if char not in string.punctuation or char == allowed_punct else " " for char in text)
    text = text.replace("\u00AB", "").replace("\u00BB", "").replace("\u0384", "").replace("\u2019", "")

    docs.append(text)


output_path = script_dir / 'docs_data.txt'

with open(output_path, 'w', encoding='utf-8') as f:
    for doc in docs:
        f.write(doc + '\n')  # Each document on a new line


# From now on you can work with the list named docs
# which contains basically terms that are going to
# be inserted in the inverted index