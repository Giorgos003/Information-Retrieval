import os
import heapq
from collections import defaultdict
import pickle
import math
import Preprocess_tools as tools
import pandas as pd
import sqlite3
import sys
import heapq
import time
import spacy


class InvertedIndex:
    def __init__(self, temp_dir=None):
        """
        Initialize the inverted index.
        :param temp_dir: Directory to store temporary files. Defaults to system temp directory.
        """

        # In-memory index: stores term -> {'doc_ids': {doc_id: term_freq}}
        self.index = defaultdict(dict)
        self.lengths = defaultdict()
        self.num_of_docs = 0


    def create_index_from_csv(self, input_file, create_db=False):
        if create_db:
            conn = sqlite3.connect("data.db")

        reader = pd.read_csv(input_file, chunksize=10000)

        for i, df_chunk in enumerate(reader):
            print(f'chunk {i}')

            df = df_chunk
            df.index.name = 'id'
            df = tools.filter_dataframe(df)

            if create_db:
                # Write chunk to db
                df.to_sql('unfiltered_records', conn, if_exists='append')
                print(f"chunk {i} is written to the database")

            # Preprocess it 
            doc_ids, preprocessed_list = tools.df_preprocess(df)

            self.num_of_docs += len(doc_ids)


            for id, record in zip(doc_ids, preprocessed_list):
                # Tokenize record
                terms = tools.stopword_removal(record.strip().split())
                
                unique_terms = set()
                for term in terms:
                    stemmed_word = tools.basic_stemmer(term)
                    unique_terms.add(stemmed_word)

                    self.update_catalog(stemmed_word, id)

                self.lengths[id] = len(unique_terms)

            

        if create_db:
            try: conn.close()
            except: print("db connection didn't close successfully")


        conn = sqlite3.connect("data.db")
        conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT, value BLOB)")
        for key , value in self.index.items():
            conn.execute("INSERT INTO kv VALUES (?, ?)", (key, pickle.dumps(value)))


        conn.commit()
        conn.close()

        del(self.index)
        self.index = defaultdict(dict)



    

    def update_catalog(self, term, doc_id):

        if term in self.index:
            if doc_id in self.index[term]:
                self.index[term][doc_id] += 1
            else:
                self.index[term][doc_id] = 1
                
        else:
            self.index[term] = {doc_id:1}

    def search_query(self, query:str, k:int=10)->list:
        # Preprocess query 
        preprocessed_query = tools.document_preprocess(query)

        # Tokenize query and remove stopwords
        query_terms = tools.stopword_removal(preprocessed_query.strip().split())

        # Stem the query
        temp = []
        for term in query_terms:
            temp.append(tools.basic_stemmer(term))
        query_terms = temp

        # # Update catalog and precompute useful values
        # self.num_of_docs += 1
        # query_id = self.num_of_docs     

        # # MAYBE OPTIONAL
        # for term in query_terms:
        #     self.update_catalog(term, query_id)


        query_set = set(query_terms)

        # Filter terms with low idf values
        # threshold = tools.IDF(n=self.num_of_docs/2 , N=self.num_of_docs)

        # max_idf = 0
        # max_term = None

        # temp_set = query_set.copy()
        # for term in query_set:
        #     idf = tools.IDF(len(self.index[term]) , self.num_of_docs)

        #     if idf > max_idf:
        #         max_idf = idf
        #         max_term = term

        #     if idf < threshold:
        #         temp_set.remove(term)

        # # Handle queries with only frequent terms
        # if not temp_set:
        #     temp_set.add(max_term)

        # query_set = temp_set
        

        print(f"query set reduced to {query_set}")

        # Retrieve terms from index
        conn = sqlite3.connect("data.db")
        for key in query_set:
            res = conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
            value = pickle.loads(res[0]) if res else None
            self.index[key] = value

        conn.close()
        


        




        q_terms_idfs = []
        for term in query_set:
            idf = tools.IDF(n=len(self.index[term]) , N=self.num_of_docs)
            print(f"{(idf,term)}")
            q_terms_idfs.append((idf,term))

        
        q_terms_idfs = sorted(q_terms_idfs, reverse=True)
        accumulators = defaultdict()

        for idf, term in q_terms_idfs:
            for doc_id, freq in self.index[term].items():
                score = tools.TF(freq) * idf / self.lengths[doc_id]
                accumulators[doc_id] = accumulators.get(doc_id, 0) + score

        top_k_items = sorted(accumulators.items(), key=lambda item: item[1], reverse=True)[:k]

        
        return top_k_items

    
    
    def save_index(self, file_path):
        """
        Save the inverted index to a file.
        :param file_path: Path to save the index.
        """
        print(f"TEST {self.index}")

        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self, f)
        except:
            print('error saving the index to pickle form')

    def load_index(self, file_path):
        """
        Load the inverted index from a file.
        :param file_path: Path to load the index.
        """
        with open(file_path, 'rb') as f:
            obj = pickle.load(f)

        print(f"TEST {obj.index}")
        
        return obj
