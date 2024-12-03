import re
from collections import defaultdict

# Sample documents (Replace with your own data)
documents = {
    1: "In the twilight of the 13th century, the kingdom of Eldermarch stood strong.",
    2: "The knights of Eldermarch defended their lands with valor and loyalty.",
    3: "An army of invaders threatened to conquer the kingdom and end its reign."
}

# Function to preprocess text (removes punctuation and converts to lowercase)
def preprocess(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.lower()

# Function to create an inverted index
def create_inverted_index(docs):
    inverted_index = defaultdict(list)
    for doc_id, content in docs.items():
        words = preprocess(content).split()  # Tokenize the content
        for position, word in enumerate(words):
            inverted_index[word].append((doc_id, position))
    return inverted_index

# Create the inverted index
inverted_index = create_inverted_index(documents)

# Display the inverted index
print("Inverted Index:")
for term, postings in inverted_index.items():
    print(f"{term}: {postings}")
