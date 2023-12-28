import math
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from file_retriever import load_file

from flask import Flask, request, jsonify


app = Flask(__name__)


lexicon = load_file("lexicon.json")
no_of_words_per_barrel = 1000

def printlist(list):
    for item in list:
        print(item)

def proximity_rank(doc, word_ids):
    val = 0
    if doc:
        #Initialize with the positions of the first term
        initial_positions = doc[word_ids[0]]

        for pos in initial_positions:
            #Check if there are consecutive positions for the remaining terms
            if all(pos + i in doc[word_id] for i, word_id in enumerate(word_ids[1:], start=1)):
                val += 10  # Increment rank for each valid phrase occurrence

    return min(val, 100)


def calculate_rank(doc, word_ids):
    rank = 0
    rank += 0.4 * math.log(1 + proximity_rank(doc, word_ids))
    for item in doc:
        tf = len(item["t"]) + len(item["c"]) + len(item["a"]) + len(item["s"])
        if item["t"]:
            rank += min(math.log(1 + 1 * len(item["t"])) / tf, 0.20) / len(word_ids)
        if item["c"]:
            rank += min(math.log(1 + 0.3 * len(item["c"])) / tf, 0.20) / len(word_ids)
        if item["a"]:
            rank += min(math.log(1 + 0.9 * len(item["a"]) / tf), 0.20) / len(word_ids)
        if item["s"]:
            rank += min(math.log(1 + 0.8 * len(item["s"]) / tf), 0.20) / len(word_ids)

    return rank



def find(word_ids):
    docs = {}
    rank = {}
    words = []
    barrel_id = -1
    sorted_word_ids = sorted(word_ids)
    for word_id in sorted_word_ids:
        if barrel_id != word_id // 1000:
            barrel_id = word_id // 1000
            barrel = load_file(f"inverted_index_barrel{barrel_id}.json")
        if word_id in barrel: #re-consider this#
            data = barrel[word_id]
            words.append(data)
    for word_key, word in words:
        for item_key, item in word:
            docs[item_key][word_key] = word
    for doc_key, doc in docs:
        rank[doc_key] = calculate_rank(doc, word_ids)
    return rank



def search(query):
    tokens = word_tokenize(query.lower())
    if not tokens:
        return
    word_ids = []
    for token in tokens:
        if token not in stopwords.words('english'):
            word_id = lexicon[token]
            word_ids.append(word_id)
    return find(word_ids)

@app.route('/search', methods=['POST'])
def api_search():
    content = request.json
    query = content.get('query', '')
    if query:
        results = search(query)
        return jsonify(results)
    else:
        return jsonify({"error": "No query provided"}), 400


docs = search("hello for world")

sorted_items = sorted(docs.items(), key=lambda item: item[1])

def display(docs, size, offset):
        doc_data = []
        start_index = offset * size
        end_index = start_index + size

        # Extract the desired range of documents
        selected_keys = list(docs.keys())[start_index:end_index]

        for key in selected_keys:
            barrel_id = -1
            if barrel_id != key // 1000:
                barrel_id = key // 1000
                barrel = load_file(f"metadata/metadata_barrel_{barrel_id}.json")
            doc_data.append(barrel[key])
        return doc_data


@app.route('/display', methods=['POST'])
def api_display():
    content = request.json
    docs = content.get('docs', {})
    size = int(content.get('size', 10))
    offset = int(content.get('offset', 0))

    if docs:
        doc_data = display(docs, size, offset)
        return jsonify(doc_data)
    else:
        return jsonify({"error": "No documents provided"}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3001, debug=True)