import math
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from file_retriever import load_file

lexicon = load_file("lexicon.json")


def printlist(list):
    for item in list:
        print(item)

def dynamic_num_words_func(counter):
    if counter <= 20000:
        return 100
    elif counter <= 100000:
        return 10000
    else:
        return 20000

def proximity_rank(doc, word_ids):
    val = 0
    if doc and all(word_ids[0] in doc for word_id in word_ids):
        # Initialize with the positions of the first term
        initial_positions = doc[word_ids[0]]

        for pos_type, positions_list in initial_positions.get("p", {}).items():

            # Iterate over each position of the first term
            for pos in positions_list:
                valid_occurrence = True

                # Check if there are consecutive positions for the remaining terms
                for i, word_id in enumerate(word_ids[1:], start=1):
                    if pos + i not in doc.get(word_id, {}).get("p", {}).get(pos_type, []):
                        valid_occurrence = False
                        break  # No need to check further positions for this occurrence

                if valid_occurrence:
                    val += 10  # Increment rank for each valid phrase occurrence

    return min(val, 100)




def calculate_rank(doc, word_ids):
    rank = 0
    if len(word_ids) > 1:
        rank += 0.35 * math.log(1 + proximity_rank(doc, word_ids))

    for key, item in doc.items():
        p_data = item.get("p", {})
        tf = len(p_data.get("t", [])) + len(p_data.get("c", [])) + len(p_data.get("a", [])) + len(p_data.get("s", []))
        if p_data.get("t"):
            rank += min(math.log(1 + 1 * len(p_data["t"])) / tf, 0.20) / len(word_ids)
        if p_data.get("c"):
            rank += min(math.log(1 + 0.3 * len(p_data["c"])) / tf, 0.20) / len(word_ids)
        if p_data.get("a"):
            rank += min(math.log(1 + 0.9 * len(p_data["a"]) / tf), 0.20) / len(word_ids)
        if p_data.get("s"):
            rank += min(math.log(1 + 0.8 * len(p_data["s"]) / tf), 0.20) / len(word_ids)
    return rank



def find(word_ids):
    docs = defaultdict(dict)
    rank = {}
    words = {}
    barrel_id = -1
    sorted_word_ids = sorted(word_ids)
    print(sorted_word_ids)
    for word_id in sorted_word_ids:
        no_of_words_per_barrel = dynamic_num_words_func(word_id)
        if barrel_id != word_id // no_of_words_per_barrel:
            barrel_id = word_id // no_of_words_per_barrel
            barrel = load_file(f"inverted_index/inverted_index_barrel_{barrel_id}.json")
        if str(word_id) in barrel:
            data = barrel[str(word_id)]
            words[word_id] = data

    for word_key, word in words.items():
        for item_key, item in word.items():
            docs[item_key][word_key] = item
    for doc_key, doc in docs.items():
        rank[doc_key] = calculate_rank(doc, word_ids)
    return rank



def search(query):
    tokens = word_tokenize(query.lower())
    special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '[', ']', '{', '}', ';',
                          ':', ',', '.', '<', '>', '/', '?', '|', '\\', '`', '~']

    if not tokens:
        return
    word_ids = []
    for token in tokens:
        if token not in stopwords.words('english') and token not in special_chars:
            word_id = lexicon[token]
            word_ids.append(word_id)
    return find(word_ids)


docs = search("Richest Man")
sorted_items = sorted(docs.items(), key=lambda item: item[1], reverse=True)
print(f"{len(sorted_items)} articles retrieved")

def display(docs, size, offset):
    doc_data = []
    start_index = offset * size
    end_index = start_index + size

    # Extract the desired range of document IDs and ranks
    selected_items = sorted_items[start_index:end_index]

    for doc_id, rank in selected_items:
        barrel_id = -1
        if barrel_id != int(doc_id) // 1000:
            barrel_id = int(doc_id) // 1000
            barrel = load_file(f"metadata/metadata_barrel_{barrel_id}.json")
        doc_data.append(barrel[doc_id])

    return doc_data

result = display(sorted_items, 10, 0)

printlist(result)