from Inverted_Index import InvertedIndex
import Preprocess_tools as tools
import sys
import time



# Initialize the InvertedIndex class
inverted_index = InvertedIndex()

# Path to the csv file
input_file = "Greek_Parliament_Proceedings_1989_2020.csv"


# Create the index from the input file
# ----------------------------------------
start = time.time()
inverted_index.create_index_from_csv(input_file, create_db=False) # create_db should be True for the first time
end = time.time()
print(f"\nIndex created in {end-start:.0f} seconds")

print(f"number of unique keys: {len(inverted_index.index.keys())}")


# Save the index
# ----------------------------------------
inverted_index.save_index("inverted_index.pkl")


# Load the index
# ----------------------------------------
# start = time.time()
# inverted_index.load_index("inverted_index.pkl")
# inverted_index.num_of_docs = 706801 # num of actual docs in db, should be calculated automatically
# end = time.time()
# print(f"Catalog loaded in {end-start:.1f} sec")


# Search query
# ----------------------------------------
query = 'παλαιστίνη'

start = time.time()
inverted_index.search_query(query)
end = time.time()
print(f"Query executed in {end-start:.6f} sec")