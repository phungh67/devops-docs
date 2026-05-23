import numpy as np
import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

sys.path.append(project_root)

from classes.vector_db import VectorDatabase 

def construct_vocabulary(set_of_sentences):
    """Construct vocabulary from a predefined set of sentences
    Keyword arguments:
    set_of_sentences -- a string array
    Return: a set of words 
    """
    vocabulary = set()
    for sentence in set_of_sentences:
        tokens = sentence.lower().split()
        vocabulary.update(tokens)
    return vocabulary

def construct_word_indexes(vocabulary):
    """Index the words within created vocabulary
    Keyword arguments:
    vocabulary -- set of words (string)
    Return: a dictionary of words and indexes
    """
    word_index = {word: i for i, word in enumerate(vocabulary)}
    return word_index

def vectorized_sentence(sentence, word_index, vocabulary):
    """Vectorized a sentece with a given word_index and a vocabulary
    Keyword arguments:
    scentence -- a string input
    word_index -- words with indexes
    vocabulary -- set of unique words generated from pre defined database, for vector's length
    Return: a vector with dimensions are equal to one's vocabulary   
    """
    vectorized_result = np.zeros(len(vocabulary))
    for token in sentence.lower().split():
        if token in word_index:
            vectorized_result[word_index[token]] += 1
    return vectorized_result

def vectorized_input_database(set_of_sentences, word_index, vocabulary):
    """Vectorized the input strings database
    
    Keyword arguments:
    set_of_sentences -- a set of strings
    word_index -- a dictionary of words with indexes
    vocabulary -- the set created from unique words extracted from set_of_sentences
    Return: a dictionary of each sentences with vectorized words
    """
    sentence_vectors = {}
    for sentence in set_of_sentences:
        vector = vectorized_sentence(sentence, word_index, vocabulary)
        sentence_vectors[sentence] = vector
    return sentence_vectors

if __name__ == "__main__":
    vocabulary = construct_vocabulary(sentences)

    word_index = construct_word_indexes(vocabulary)

    sentence_vectors = vectorized_input_database(sentences, word_index, vocabulary)

    vector_db = VectorDatabase()
    for sentence, vector in sentence_vectors.items():
        vector_db.add_vector(sentence, vector)

    query_sentence = "After the incident, I need to inspect security credential, retrieve it for me"
    query_vector = vectorized_sentence(query_sentence, word_index, vocabulary)

    similar_sentences = vector_db.find_similar_vectors(query_vector, num_results=2)

    print("Query Sentence:", query_sentence)
    print("Similar Sentences:")
    for sentence, similarity in similar_sentences:
        print(f"{sentence}: Similarity = {similarity:.4f}")