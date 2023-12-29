import json
import threading
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

import file_retriever
from file_retriever import get_json_file_paths
from file_retriever import load_file
import check_url

def load_inverted_index():
    inverted_index = {}
    barrel_id = 0
    while True:
        filename = f"inverted_index/inverted_index_barrel_{barrel_id}.json"
        if os.path.exists(filename):
            inverted_index.update(load_file(filename))
            barrel_id += 1

        else:
            return inverted_index


def build_index():
    inverted_index = load_inverted_index()
    barrel_id =0
    while True:
        filename = f"forward_index/forward_index_barrel_{barrel_id}.json"

        if os.path.exists(filename):
            forward_index = load_file(filename)
            print(f"Processed {filename}. Progress: {barrel_id} files.")

            for doc_id, doc_data in forward_index.items():
                for term, postings in doc_data['w'].items():
                    if term not in inverted_index:
                        inverted_index[term] = {}

                    if doc_id not in inverted_index[term]:
                        inverted_index[term][doc_id] = postings

            barrel_id += 1

        else:
            return inverted_index

def dynamic_num_words_func(counter):
    if counter <= 20000:
        return 100
    elif counter <= 100000:
        return 10000
    else:
        return 20000

def divide_into_barrels(words):
    barrels = []
    current_barrel = {}
    counter = 0
    words_counter = 0
    for doc_id, doc_data in words.items():
        current_barrel[doc_id] = doc_data
        counter += 1
        words_counter +=1
        if counter == dynamic_num_words_func(words_counter):
            barrels.append(current_barrel)
            current_barrel = {}
            counter = 0

    if current_barrel:
        barrels.append(current_barrel)

    return barrels

def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

def save_barrels(barrels, base_filename):
    for i, barrel in enumerate(barrels):
        filename = f"{base_filename}_{i}.json"
        save_to_json(barrel, filename)



inverted_index = build_index()

sorted_inverted_index = dict(sorted(inverted_index.items(), key=lambda item: int(item[0])))
barrels = divide_into_barrels(sorted_inverted_index)
save_barrels(barrels, 'inverted_index/inverted_index_barrel')