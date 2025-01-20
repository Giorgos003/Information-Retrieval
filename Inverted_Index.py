import os
import heapq
import tempfile
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
        # self.temp_dir = temp_dir or tempfile.gettempdir()
        # self.temp_files = []

        # In-memory index: stores term -> {'doc_ids': {doc_id: term_freq}}
        self.index = defaultdict(dict)
        self.lengths = defaultdict()
        self.num_of_docs = 0


    def _write_temp_file(self, term_doc_pairs):
        pass
        # """
        # Write term-document pairs to a temporary file.
        # :param term_doc_pairs: List of (term, doc_id, term_freq) pairs.
        # """
        # temp_file = tempfile.NamedTemporaryFile(delete=False, dir=self.temp_dir, mode='w')
        # temp_file_name = temp_file.name

        # for term, doc_id, term_freq in term_doc_pairs:
        #     temp_file.write(f"{term}\t{doc_id}\t{term_freq}\n")

        # temp_file.close()
        # self.temp_files.append(temp_file_name)

    def create_index_from_file(self, input_file):
        pass
        # """
        # Create an inverted index from a text file, where each line is a document.
        # :param input_file: Path to the text file.
        # """
        # with open(input_file, 'r', encoding='utf-8') as f:
        #     for doc_id, line in enumerate(f, start=1):
        #         terms = line.strip().split()  # Tokenize the line into terms
        #         term_freqs = defaultdict(int)

        #         # print(doc_id)
        #         # Count the frequency of each term in the document
        #         for term in terms:
        #             stemmed_term = tools.basic_stemmer(term)  # Stem each term
        #             term_freqs[stemmed_term] += 1

        #         # Create term-doc pairs with frequency count
        #         term_doc_pairs = [(term, doc_id, freq) for term, freq in term_freqs.items()]
        #         self._write_temp_file(term_doc_pairs)































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

        # Update catalog and precompute useful values
        self.num_of_docs += 1
        query_id = self.num_of_docs     

        # MAYBE OPTIONAL
        for term in query_terms:
            self.update_catalog(term, query_id)


        query_set = set(query_terms)

        # Filter terms with low idf values
        threshold = tools.IDF(n=self.num_of_docs/2 , N=self.num_of_docs)

        max_idf = 0
        max_term = None

        temp_set = query_set.copy()
        for term in query_set:
            idf = tools.IDF(len(self.index[term]) , self.num_of_docs)

            if idf > max_idf:
                max_idf = idf
                max_term = term

            if idf < threshold:
                temp_set.remove(term)

        # Handle queries with only frequent terms
        if not temp_set:
            temp_set.add(max_term)

        query_set = temp_set
        

        print(f"query set reduced to {query_set}")
        
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


























        

        l2_query = 0
        for term in query_set:
            
            # print(f"term {term} with {len(self.index[term])}, {self.index[term]}")
            tf = tools.TF(self.index[term][query_id])
            idf = tools.IDF(len(self.index[term]) , self.num_of_docs)
            print(f"term:{term} idf:{idf}")
            
            
            l2_query += (tf*idf)**2

        # Find related docs
        doc_set = set()
        for term in terms:
            stemmed_term = tools.basic_stemmer(term)
            # stemmed_terms.append(stemmed_term)

            if not self.index :
                print('Catalog is empty')
            else:
                # print(f"Term {stemmed_term} is in {len(self.index[stemmed_term])} docs")
                temp_set = set( self.index[stemmed_term].keys() )
                doc_set = doc_set.union(temp_set)

        print(f"related docs = {len(doc_set)}")
        



        # Retrieve related docs in chunks
        max_heap = []
        doc_list = list(doc_set)

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        chunk_size = 1000
        for i in range(0 , len(doc_list) , chunk_size):
            chunk = doc_list[i : i+chunk_size]

            placeholders = ', '.join(['?'] * len(chunk))
            sql_query = f"SELECT * FROM unfiltered_records WHERE id IN ({placeholders})"
            cursor.execute(sql_query, list(chunk))

            # TO_DO: optionally delete doc_set
            results = cursor.fetchall()

            


            # Rank related docs
    
            for record in results:
        

                id = record[0]
                broken_down = record[1:]

                whole_row = ' '.join(map(str, broken_down))
                text = tools.document_preprocess(whole_row)
                terms = text.strip().split()

                refined_terms = tools.stopword_removal(terms)

                unique_terms = {tools.basic_stemmer(term) for term in refined_terms}
                
                l2_doc = 0
                for term in unique_terms:
                    try:
                        tf = tools.TF(self.index[term][id])
                        idf = tools.IDF(len(self.index[term]) , self.num_of_docs)
                    except:
                        continue
                    
                    l2_doc += (tf*idf)**2

          

                common_terms = unique_terms.intersection(query_set)
                
                internal_product = 0
                for term in common_terms:
                    # IDF should be common for the same term
                    idf = tools.IDF(len(self.index[term]) , self.num_of_docs)

                    tf = tools.TF(self.index[term][query_id])
                    w_query = tf * idf

                    tf = tools.TF(self.index[term][id])
                    w_doc = tf * idf

                    internal_product += w_query * w_doc

                score = internal_product/(l2_doc*l2_query)

                heapq.heappush(max_heap, (-score,id))


            


        conn.close()

        return max_heap
        for i in range(min(k, len(max_heap))):
                score, id = heapq.heappop(max_heap)
                print(f"{i+1}: doc {id} with score {-score}")




          
       
            

        


















































    def _merge_temp_files(self):
        pass
        # """
        # Merge all temporary files into a single sorted file using external merge sort.
        # """
        # temp_sorted_file = os.path.join(self.temp_dir, "merged_terms.txt")
        # with open(temp_sorted_file, 'w') as out_file:
        #     heap = []
        #     batch_size = 4000
        #     rest = 0 if len(self.temp_files)%batch_size == 0 else 1
        #     for i in range(len(self.temp_files)//batch_size + rest):
        #         print(i)
        #         # Open all temp files for reading
        #         if i >= len(self.temp_files)//batch_size:
        #             temp_file_objects = [open(f, 'r') for f in self.temp_files[i*batch_size:]]

        #         temp_file_objects = [open(f, 'r') for f in self.temp_files[i*batch_size:(i+1)*batch_size]]

        #         # Create a heap to merge sorted streams
        #         # heap = []
        #         for file_id, file_obj in enumerate(temp_file_objects):
        #             line = file_obj.readline()
        #             if line:
        #                 # Ensure the line contains exactly three values
        #                 parts = line.strip().split('\t')
        #                 if len(parts) == 3:
        #                     term, doc_id, term_freq = parts
        #                     heapq.heappush(heap, (term, int(doc_id), int(term_freq), file_id))
        #     print(f"len of heap: {len(heap)}")
        #     while heap:
        #         term, doc_id, term_freq, file_id = heapq.heappop(heap)
        #         out_file.write(f"{term}\t{doc_id}\t{term_freq}\n")

        #         # Read the next line from the same file
        #         print(file_id)
        #         next_line = temp_file_objects[file_id].readline()
        #         if next_line:
        #             parts = next_line.strip().split('\t')
        #             if len(parts) == 3:  # Ensure we have the correct number of values
        #                 next_term, next_doc_id, next_term_freq = parts
        #                 heapq.heappush(heap, (next_term, int(next_doc_id), int(next_term_freq), file_id))

        # # Close and delete temporary files
        # # for f in temp_file_objects:
        # #     f.close()
        # # for f in self.temp_files:
        # #     os.remove(f)

        # self.temp_files = [temp_sorted_file]

    def build_index(self):
        pass
        # """
        # Build the final inverted index from sorted terms in the temporary file.
        # """
        # if len(self.temp_files) > 1:
        #     self._merge_temp_files()

        # # Read from the merged file and create the inverted index
        # final_index = defaultdict(dict)
        # with open(self.temp_files[0], 'r') as f:
        #     for line in f:
        #         term, doc_id, term_freq = line.strip().split('\t')
        #         doc_id = int(doc_id)
        #         term_freq = int(term_freq)

        #         if doc_id not in final_index[term]:
        #             final_index[term][doc_id] = term_freq
        #         else:
        #             final_index[term][doc_id] += term_freq  # Aggregating term frequency if term appears more than once in the same document

        # self.index = final_index
        # os.remove(self.temp_files[0])
        # self.temp_files = []

    def save_index(self, file_path):
        """
        Save the inverted index to a file.
        :param file_path: Path to save the index.
        """
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
        
        return obj

    def search(self, term):
        pass
        # """
        # Search for a term in the inverted index.
        # :param term: The term to search for.
        # :return: A dictionary containing term frequencies for each document containing the term.
        # """
        # term_data = self.index.get(term, None)
        # if term_data:
        #     return term_data
        # return None


    def print_index_to_file(self, output_file):
        pass
        # """
        # Print the inverted index to a text file.
        # :param output_file: Path to the output text file.
        # """
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     for term, doc_data in self.index.items():
        #         # Format: term -> {doc_id: term_freq}
        #         f.write(f"{term} -> {dict(doc_data)}\n")


# Example Usage
if __name__ == "__main__":

    # Initialize the InvertedIndex class
    inverted_index = InvertedIndex()

    # Path to the text file where each line is a document
    input_file = "docs_data.txt"  # Replace with your actual file path

    # Create the index from the input file
    inverted_index.create_index_from_file(input_file)

    # Build the final index
    inverted_index.build_index()

    # Save the index
    inverted_index.save_index("inverted_index.pkl")

    import sys
    sys.exit()

    # Load the index
    inverted_index.load_index("inverted_index.pkl")

    # Search for terms
    stemmed_word = tools.basic_stemmer("Βουλευτής")
    result = inverted_index.search(stemmed_word)  # Replace with a term to search
    if result:
        print(f"Term Frequencies: {result}")
    else:
        print("Term not found in index.")

    # Print the inverted index to a file
    inverted_index.print_index_to_file("inverted_index_output.txt")
