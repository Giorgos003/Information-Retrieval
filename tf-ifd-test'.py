from sklearn.feature_extraction.text import TfidfVectorizer

# Sample documents
documents = [
    "In the twilight of the 13th century, the kingdom of Eldermarch stood strong.",
    "The knights of Eldermarch defended their lands with valor and loyalty.",
    "An army of invaders threatened to conquer the kingdom and end its reign."
]

# Step 1: Initialize the TfidfVectorizer
vectorizer = TfidfVectorizer()

# Step 2: Fit and transform the documents to compute TF-IDF scores
tfidf_matrix = vectorizer.fit_transform(documents)

# Step 3: Get feature names (words) and TF-IDF scores
feature_names = vectorizer.get_feature_names_out()
tfidf_scores = tfidf_matrix.toarray()

# Step 4: Display the TF-IDF scores
print("TF-IDF Scores:")
for doc_index, doc_scores in enumerate(tfidf_scores):
    print(f"\nDocument {doc_index + 1}:")
    for word_index, score in enumerate(doc_scores):
        if score > 0:  # Display only non-zero scores
            print(f"{feature_names[word_index]}: {score:.4f}")
