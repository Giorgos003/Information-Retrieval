import json
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import normalize


def clustering():
    """
    This function performs document clustering on a set of documents represented by their vectors in a reduced latent
    semantic space, using the Mini-Batch K-Means algorithm with cosine similarity. The goal of this function
    is to group documents into clusters based on their semantic similarity.

    At the end, it prints the clusters of each document

    :return: nothing
    """
    # For start, we read the json file that we made tha mapping with the document IDs
    with open("doc_id_mapping.json", "r") as f:
        doc_id_to_index = json.load(f)

    print("Document ID mapping loaded successfully.")


    # We want to create a reverse mapping of the previous mapping so we can take the back the actual ID of each document
    # when we will need it


    # Reverse the mapping
    index_to_doc_id = {v: k for k, v in doc_id_to_index.items()}

    print("Reverse mapping made successfully")

    del doc_id_to_index





    # We load the U matrix from the SVD.
    # As you can see in our SVD implementation kn LSA.py, we save the matrices U, Σ and V^T in the svd_results.npz file/

    svd_data = np.load("svd_results.npz", mmap_mode="r")
    U = svd_data["U"]  # each row is a document vector
    print("Matrix U has been loaded")





    # For the clustering, with decided to use a quicker version of K-means, in combination with cosine similarity
    # for more accurate results


    # Normalize U matrix to unit vectors
    # This ensures cosine similarity can be approximated by Euclidean distance
    U = normalize(U, norm='l2', axis=1)  # Normalize rows to have unit length




    # Use Mini-Batch K-Means
    # We decided to use K-means, but for more speed we used the Mini Batch version of the algorithm using the
    # Python's library sklearn
    # We arbitrary select the number of cluster. Keeping in mind that the total number of documents are ~700,000
    kmeans = MiniBatchKMeans(n_clusters=100, batch_size=5000, random_state=42)
    labels = kmeans.fit_predict(U)

    print("K-means clustering labels:")





    # We want to print the cluster that each document was placed, but we want to print its actual ID. That's why we
    # use our reversed map that we constructed in the start.
    # There are total of 700,000, of course we can't print them all. We print the 1,000 first
    for i in range(1000):
        print("Document with ID: ", index_to_doc_id[i], "goes on cluster: ", labels[i])


clustering()