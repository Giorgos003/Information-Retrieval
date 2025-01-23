from Inverted_Index import InvertedIndex
import time

# Path to the csv file
input_file = "Greek_Parliament_Proceedings_1989_2020.csv"

# Initialize the InvertedIndex class
catalog = InvertedIndex()

# Create the index from the input file
# ----------------------------------------
start = time.time()
catalog.create_index_from_csv(input_file, True) # create_db should be True for the first time
end = time.time()
print(f"\nIndex created in {end-start:.0f} seconds")

# Save the index
# ----------------------------------------
catalog.save_index("inverted_index.pkl")