import csv

import numpy as np
import scipy.sparse as sp
from sklearn.decomposition import TruncatedSVD
import json


import  Inverted_Index
import time
import sqlite3
import pickle
import numpy
import Preprocess_tools as tools



from test_main import inverted_index


def find_optimal_k(term_doc_matrix, energy_threshold=0.9):
    """
    Dynamically determine the number of components (k) based on the cumulative energy.

    Parameters:
    - term_doc_matrix: The term-document matrix (in sparse or dense format).
    - energy_threshold: The proportion of total energy to capture (default is 90%).

    Returns:
    - k: The optimal number of components.
    """
    # Perform SVD on the term-document matrix (without truncation)
    # This function takes
    svd = TruncatedSVD(n_components=min(term_doc_matrix.shape), random_state=42)
    svd.fit(term_doc_matrix)

    # Singular values represent the "energy" of each component
    singular_values = svd.singular_values_

    # Calculate the cumulative sum of singular values (energy)
    cumulative_energy = np.cumsum(singular_values ** 2)
    total_energy = cumulative_energy[-1]  # Total energy is the sum of squares of all singular values

    # Find the optimal k based on the energy threshold
    k = np.argmax(cumulative_energy >= energy_threshold * total_energy) + 1

    return k



def lsa():
    """
    This function implements Latent Semantic Analysis (LSA) on the documents of the database.

    1. Loads an inverted index and retrieves document-term relationships from a database.
    2. Constructs a sparse term-document matrix efficiently.
    3. Computes the sparsity of the matrix.
    4. Determines the optimal number of dimensions (topics) for SVD.
    5. Performs Truncated SVD to reduce dimensionality.
    6. Saves the transformed matrices for further use.

    :return: the U, Σ, V^T matrices of the Singular Value Decomposition of the term-to-doc matrix
    """

    # We are loading the inverted index so we can extract the terms and documents from the database more easily

    # Path to the csv file
    input_file = "Greek_Parliament_Proceedings_1989_2020.csv"

    # Initialize the InvertedIndex class
    print(f"started loading catalog")
    import time
    start = time.time()

    inverted = Inverted_Index.InvertedIndex().load_index("inverted_index.pkl")
    end = time.time()
    print(f"loaded in {end - start:.1f}")

    # Load full catalog from the SQLite database
    conn = sqlite3.connect("data.db")
    cursor = conn.execute("SELECT key, value FROM kv")
    for key, value in cursor.fetchall():
        inverted.index[key] = pickle.loads(value)
    conn.close()

    # We print the number of terms that are in the inverted index
    print(f"Full catalog loaded with {len(inverted.index)} terms.")




    # We compute and print the total number of the documents
    N = inverted.num_of_docs
    print("The total number of documents are: ", N)

    """ The total number of terms are: 446601 and the total number of docs are: 706801 """







    # The preprocessing of the data deleted some documents, so from the ~1,200,000 documents, only ~700,000 left. But
    # their IDs might be greater than 700K and up to 1,2M. So, we match every document with a new ID that belongs to [0, ~700,000]

    # By this way, we can have a 1-1 matching between the rows of the doc-to-term matrix that we want to construct
    # and the documents IDs


    # Extract unique document IDs
    all_document_ids = {}

    for i, (term, doc_ids) in enumerate(inverted.index.items()):
        for doc_id, freq in doc_ids.items():
            all_document_ids[doc_id] = True  # Storing unique document IDs

    # Sort the document IDs
    sorted_doc_ids = sorted(all_document_ids.keys())  # Sorted list of unique document IDs

    # Create a mapping from document IDs to indices (0 to N-1)
    doc_id_to_index = {doc_id: i for i, doc_id in enumerate(sorted_doc_ids)}

    # Save the mapping as a JSON file so we can use it in our data clustering
    with open("doc_id_mapping.json", "w") as f:
        json.dump(doc_id_to_index, f)

    print("Document ID mapping saved successfully.")


    del sorted_doc_ids
    print()



    # Here we start constructing the doc-to-term matrix as memory efficiently as possible.

    row_indices = []
    col_indices = []
    values = []


    # We enumerate each term of the inverted index so we can compute tha tf-idf values
    for i, (term, doc_ids) in enumerate(inverted.index.items()):

        # Compute the idf value
        idf = tools.IDF(len(doc_ids), N)

        row = i

        for doc_id, freq in doc_ids.items():

            tf = tools.TF(freq)

            if doc_id in doc_id_to_index:
                col = doc_id_to_index[doc_id]
                row_indices.append(row)
                col_indices.append(col)
                values.append(freq)


    # We convert to sparse matrix using COO format
    num_terms = len(inverted.index)
    num_docs = N

    print("Building sparse matrix...")
    term_doc_matrix = sp.coo_matrix((values, (row_indices, col_indices)), shape=(num_terms, num_docs), dtype=np.float32)

    # Convert to a more efficient format (Compressed Sparse Row)
    print("Converting to CSR format...")
    term_doc_matrix = term_doc_matrix.tocsr()

    # Save the entire sparse matrix efficiently
    print("Saving sparse matrix...")
    sp.save_npz("term_doc_matrix.npz", term_doc_matrix)

    print("Sparse matrix saved successfully as 'term_doc_matrix.npz'")




    # We compute and print information about the sparsity of our doc-to-term matrix.

    print("Computing the sparsity of the doc-to-term matrix")
    nnz = term_doc_matrix.nnz
    total_elements = term_doc_matrix.shape[0] * term_doc_matrix.shape[1]
    sparsity = 100 * (1 - nnz / total_elements)
    print(f"Nonzero elements: {nnz}")
    print(f"Sparsity: {sparsity:.6f}%")




    # We get ready to run the Singular Value Decomposition (SVD) to our doc-to-term matrix by computing the number of
    # dimensions that we want to reach.

    # In this step, we could use either the function find_optimal_k() to the find the optimal number of dimensions, either
    # we choose a number arbitrarily.

    # The function find_optimal_k(), to compute the optimal number of dimensions, takes a lot of time (~hours) and is not
    # recommended. It will compute approximately a k greater than 1,5K.

    # For number of k>~600 the time that it takes is huge
        # for k=300 it takes ~5 minutes
        # for k=400 it takes ~8 minutes
        # for k=500 it takes ~12 minutes
        # for k=800 it takes ~20-25 minutes

    print("Finding the optimal number of dimensions...")
    # Define the number of dimensions (topics) to keep
    # k = find_optimal_k(term_doc_matrix, 0.9)
    k = 300  # Choose based on your needs

    print("the optimal number of dimensions found: ", k)





    # Starting the Singular Values Decomposition (SVD)


    # Here, we transform our doc-to-term matrix to the term-to-doc so we can perform truncated SVD the right way
    term_doc_matrix = term_doc_matrix.T


    print("SVD starts...")


    # Initialize Truncated SVD
    svd = TruncatedSVD(n_components=k, random_state=42, algorithm="randomized")

    # Perform SVD
    U = svd.fit_transform(term_doc_matrix)  # U matrix (documents in reduced space)
    Sigma = svd.singular_values_  # Singular values
    Vt = svd.components_  # V^T matrix (terms in reduced space)

    print("SVD completed!")
    print(f"U shape: {U.shape}, Sigma shape: {Sigma.shape}, Vt shape: {Vt.shape}")


    # Save results
    np.savez("svd_results.npz", U=U, Sigma=Sigma, Vt=Vt)
    print("SVD results saved successfully!")

    print(U[:5])


    return U, Sigma, Vt




lsa()