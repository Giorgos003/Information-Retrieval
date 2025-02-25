from Inverted_Index import InvertedIndex
import time



# Initialize the InvertedIndex class
catalog = InvertedIndex()

# Path to the csv file
input_file = "Greek_Parliament_Proceedings_1989_2020.csv"


# Create the index from the input file
# ----------------------------------------
# start = time.time()
# catalog.create_index_from_csv(input_file) # create_db should be True for the first time
# end = time.time()
# print(f"\nIndex created in {end-start:.0f} seconds")

# print(f"number of unique keys: {len(inverted_index.index.keys())}")
# print(f"number of docs: {inverted_index.num_of_docs}")
# print(f"number of items in lengths: {len(inverted_index.lengths)}")


# Save the index
# ----------------------------------------
# catalog.save_index("inverted_index.pkl")


# Load the index
# ----------------------------------------
start = time.time()
catalog = InvertedIndex().load_index("inverted_index.pkl")
end = time.time()
print(f"Catalog loaded in {end-start:.1f} sec")

# Search query
# ----------------------------------------
query = 'παλαιστίνη'

start = time.time()
print(catalog.search_query(query))
end = time.time()
print(f"Query executed in {end-start:.6f} sec")