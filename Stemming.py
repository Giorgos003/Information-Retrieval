from nltk.stem import PorterStemmer

# File paths
input_file = "processed_story_words.txt"  # Input file containing processed words
output_file = "stemmed_words.txt"  # Output file for stemmed words

# Initialize the stemmer
stemmer = PorterStemmer()

# Step 1: Read words from the input file
with open(input_file, "r", encoding="utf-8") as file:
    words = file.readlines()

# Step 2: Stem each word
stemmed_words = [stemmer.stem(word.strip()) for word in words]

# Step 3: Write each stemmed word to a new line in the output file
with open(output_file, "w", encoding="utf-8") as file:
    for stemmed_word in stemmed_words:
        file.write(stemmed_word + "\n")

print(f"Stemmed words have been written to {output_file}")
