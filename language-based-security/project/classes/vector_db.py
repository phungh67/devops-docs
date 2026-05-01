import numpy as np

class VectorDatabase:
    """Definition for a Vector database with simple methods to store and retrieve
    
    add_vector(self, vector_id, vector): add a vector with vector_id to databases
    find_similar_vectors(self, query_vector, num_results): find similar vector with 'query_vector', limit results to num_of_results
    """
    
    def __init__(self):
        self.vector_data = {}
    
    def add_vector(self, vector_id, vector):
       # add an element to the data store
       self.vector_data[vector_id] = vector

    def find_similar_vectors(self, query_vector, num_results=2):
        results = []
       # calculate the cosine (undirectional multiple between 2)
        for vector_id, vector in self.vector_data.items():
            similarity = np.dot(query_vector, vector) / (np.linalg.norm(query_vector) * np.linalg.norm(vector))
            results.append((vector_id, similarity))
        # sort by looking the index x (the associated score for each vector)
        # and from bigger to smaller
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:num_results]