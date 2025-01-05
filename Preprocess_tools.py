import math
import pandas as pd
import unicodedata
import string
from nltk.stem.snowball import SnowballStemmer
from greek_stemmer import GreekStemmer

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
    ids = []
    allowed_punct = "/"

    for index, row in df.iterrows():
        ids.append(index)

        # Turning the values of the df into a whole string
        whole_row = ' '.join(map(str, row.values))

        # Preprocess that string
        text = document_preprocess(whole_row)

        # This code removes unwanted characters
        # ######################################
        # text = ''.join(char if char not in string.punctuation or char == allowed_punct else " " for char in text)
        # # Replace some weird greek punctuations
        # text = text.replace("\u00AB", "").replace("\u00BB", "").replace("\u0384", "").replace("\u2019", "").replace("\u00BE","").replace("\u2215","")

        # This code specifies which caracters to keep
        # text = text.replace("/", "-")
        


        docs.append(text)

    return ids, docs

def document_preprocess(doc):
    allowed_punct = '/'    

    text = doc.lower()
    text = remove_accents(text)

    text = text.replace("\xba", "").replace("\xbb", "").replace("\xbc", "").replace("\xbd", "").replace("\xbe", "").replace("\u0456", "")
    text = ''.join(char if (char.isalnum() or char in string.ascii_lowercase + string.ascii_uppercase 
                            or char in 'αβγδεζηθικλμνξοπρστυφχψω'  # Greek lowercase letters
                            or char in 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'  # Greek uppercase letters
                            or char == allowed_punct) else " " 
                for char in text)
    
    return text

def basic_stemmer(word):
        """
        Perform basic stemming on a Greek word by stripping common suffixes.
        :param word: The word to be stemmed.
        :return: The stemmed word.
        """
        suffixes = ['ος', 'ης', 'ες', 'οι', 'ο', 'ους', 'ου', 'ια', 'ι', 'ισ', 'ας', 'ή', 'η', 'ύ', 'ω', 'ς' , 'ων']
        for suffix in suffixes:
            if word.endswith(suffix):
                return word[:-len(suffix)]  # Strip the suffix
        return word  # Return the original word if no suffix matched

def complete_stemmer(word):
    # nlp = spacy.load("el_core_news_sm", disable=['parser', 'ner', 'tok2vec', 'tagger', 'attribute_ruler', 'lemmatizer'])
    pass

def TF(freq):
    return 1 + math.log(freq)

def IDF(n, N):
    return math.log(1 + N/n)