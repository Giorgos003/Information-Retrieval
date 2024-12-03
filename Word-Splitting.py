import string

# File paths
input_file = "Inverted-Index-Test-Data"  # Input file containing the story
output_file = "processed_story_words.txt"  # Output file for processed words

# Step 1: Read the story from the input file
with open(input_file, "r", encoding="utf-8") as file:
    story = file.read()

# Step 2: Remove punctuation and convert to lowercase
translator = str.maketrans("", "", string.punctuation)  # Translator to remove punctuation
processed_story = story.translate(translator).lower()  # Remove punctuation and convert to lowercase

# Step 3: Split the story into words
words = processed_story.split()

# Step 4: Write each word to a new line in the output file
with open(output_file, "w", encoding="utf-8") as file:
    for word in words:
        file.write(word + "\n")

print(f"Processed words have been written to {output_file}")

