import os
import heapq
import tempfile
from collections import defaultdict
import pickle
from nltk.stem.snowball import SnowballStemmer
from greek_stemmer import GreekStemmer


class InvertedIndex:
    def __init__(self, temp_dir=None):
        """
        Initialize the inverted index.
        :param temp_dir: Directory to store temporary files. Defaults to system temp directory.
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.temp_files = []
        # In-memory index: stores term -> {'doc_ids': {doc_id: term_freq}}
        self.index = defaultdict(dict)

    def basic_stemmer(self, word):
        """
        Perform basic stemming on a Greek word by stripping common suffixes.
        :param word: The word to be stemmed.
        :return: The stemmed word.
        """
        suffixes = ['ος', 'ης', 'ες', 'η', 'οι', 'ο', 'ους', 'ου', 'ια', 'ι', 'ισ', 'ας', 'ή', 'ύ', 'ω', 'ς']
        for suffix in suffixes:
            if word.endswith(suffix):
                return word[:-len(suffix)]  # Strip the suffix
        return word  # Return the original word if no suffix matched
    
    def complete_stemmer(self,word):
        print(f"word before {word}")
        stemmer = SnowballStemmer('spanish')
        stemmed_word = stemmer.stem(word)
        print(f"word after {stemmed_word}")

        return stemmed_word

    def _write_temp_file(self, term_doc_pairs):
        """
        Write term-document pairs to a temporary file.
        :param term_doc_pairs: List of (term, doc_id, term_freq) pairs.
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=self.temp_dir, mode='w')
        temp_file_name = temp_file.name

        for term, doc_id, term_freq in term_doc_pairs:
            temp_file.write(f"{term}\t{doc_id}\t{term_freq}\n")

        temp_file.close()
        self.temp_files.append(temp_file_name)

    def create_index_from_file(self, input_file):
        """
        Create an inverted index from a text file, where each line is a document.
        :param input_file: Path to the text file.
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            for doc_id, line in enumerate(f, start=1):
                terms = line.strip().split()  # Tokenize the line into terms
                term_freqs = defaultdict(int)

                # print(doc_id)
                # Count the frequency of each term in the document
                for term in terms:
                    stemmed_term = self.basic_stemmer(term)  # Stem each term
                    term_freqs[stemmed_term] += 1

                # Create term-doc pairs with frequency count
                term_doc_pairs = [(term, doc_id, freq) for term, freq in term_freqs.items()]
                self._write_temp_file(term_doc_pairs)

    def _merge_temp_files(self):
        """
        Merge all temporary files into a single sorted file using external merge sort.
        """
        temp_sorted_file = os.path.join(self.temp_dir, "merged_terms.txt")
        with open(temp_sorted_file, 'w') as out_file:
            # Open all temp files for reading
            temp_file_objects = [open(f, 'r') for f in self.temp_files]

            # Create a heap to merge sorted streams
            heap = []
            for file_id, file_obj in enumerate(temp_file_objects):
                line = file_obj.readline()
                if line:
                    # Ensure the line contains exactly three values
                    parts = line.strip().split('\t')
                    if len(parts) == 3:
                        term, doc_id, term_freq = parts
                        heapq.heappush(heap, (term, int(doc_id), int(term_freq), file_id))

            while heap:
                term, doc_id, term_freq, file_id = heapq.heappop(heap)
                out_file.write(f"{term}\t{doc_id}\t{term_freq}\n")

                # Read the next line from the same file
                next_line = temp_file_objects[file_id].readline()
                if next_line:
                    parts = next_line.strip().split('\t')
                    if len(parts) == 3:  # Ensure we have the correct number of values
                        next_term, next_doc_id, next_term_freq = parts
                        heapq.heappush(heap, (next_term, int(next_doc_id), int(next_term_freq), file_id))

        # Close and delete temporary files
        for f in temp_file_objects:
            f.close()
        for f in self.temp_files:
            os.remove(f)

        self.temp_files = [temp_sorted_file]

    def build_index(self):
        """
        Build the final inverted index from sorted terms in the temporary file.
        """
        if len(self.temp_files) > 1:
            self._merge_temp_files()

        # Read from the merged file and create the inverted index
        final_index = defaultdict(dict)
        with open(self.temp_files[0], 'r') as f:
            for line in f:
                term, doc_id, term_freq = line.strip().split('\t')
                doc_id = int(doc_id)
                term_freq = int(term_freq)

                if doc_id not in final_index[term]:
                    final_index[term][doc_id] = term_freq
                else:
                    final_index[term][doc_id] += term_freq  # Aggregating term frequency if term appears more than once in the same document

        self.index = final_index
        os.remove(self.temp_files[0])
        self.temp_files = []

    def save_index(self, file_path):
        """
        Save the inverted index to a file.
        :param file_path: Path to save the index.
        """
        with open(file_path, 'wb') as f:
            pickle.dump(self.index, f)

    def load_index(self, file_path):
        """
        Load the inverted index from a file.
        :param file_path: Path to load the index.
        """
        with open(file_path, 'rb') as f:
            self.index = pickle.load(f)

    def search(self, term):
        """
        Search for a term in the inverted index.
        :param term: The term to search for.
        :return: A dictionary containing term frequencies for each document containing the term.
        """
        term_data = self.index.get(term, None)
        if term_data:
            return term_data
        return None


    def print_index_to_file(self, output_file):
        """
        Print the inverted index to a text file.
        :param output_file: Path to the output text file.
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for term, doc_data in self.index.items():
                # Format: term -> {doc_id: term_freq}
                f.write(f"{term} -> {dict(doc_data)}\n")


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
    stemmed_word = inverted_index.basic_stemmer("Βουλευτής")
    result = inverted_index.search(stemmed_word)  # Replace with a term to search
    if result:
        print(f"Term Frequencies: {result}")
    else:
        print("Term not found in index.")

    # Print the inverted index to a file
    inverted_index.print_index_to_file("inverted_index_output.txt")



