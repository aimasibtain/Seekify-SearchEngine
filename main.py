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

file_paths = r'D:\Downloads\data\data3'

json_files = get_json_file_paths(file_paths)
#checks if file have been successfully retrieved
print(json_files)

# Mechanism for stop words
import nltk

#run only once. Remove after first execution
nltk.download('punkt')
nltk.download('stopwords')


class IndexBuilder(threading.Thread):
    def __init__(self, file_list, forward_index, lock, progress_counter, words, urls, global_doc_id, meta_data):
        threading.Thread.__init__(self)
        #initializing the object with the passed values
        self.file_list = file_list
        self.forward_index = forward_index
        self.lock = lock
        self.progress_counter = progress_counter
        self.words = words
        self.urls = urls
        self.global_doc_id = global_doc_id
        self.meta_data = meta_data
        self.special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '[', ']', '{', '}', ';', ':', ',', '.', '<', '>', '/', '?', '|', '\\', '`', '~']
    #adds words and their respective frequencies and the position and type of each occurrence for a document section
    def add(self, doc_id, tokens, type, count):
        with self.lock:
            #finds the position of each word in the section
            position = 0
            for token in tokens:
                # filters out stopwords
                if token not in stopwords.words('english') and token not in self.special_chars:
                    #checks to see if word is in our lexicon
                    if token not in self.words:
                        #if the word is not present, it is assigned an id and added to the lexicon
                        word_id = len(self.words) + 1
                        self.words[token] = word_id
                    else:
                        # if the word is found, we retrieve its id
                        word_id = self.words[token]
                    # If a list doesn't exist for the type, we initialize it
                    if type not in self.forward_index[doc_id]["w"][word_id]["p"]:
                        self.forward_index[doc_id]["w"][word_id]["p"][type] = []
                    #updating the forward index
                    self.forward_index[doc_id]["w"][word_id]["f"] += 1
                    #count is the position from which the section of the article begins
                    self.forward_index[doc_id]["w"][word_id]["p"][type].append(position+count)
                    position += 1
    def run(self):
        #iterating through every file
        for file in self.file_list:
            with open(file, 'r') as f:
                data = json.load(f)
                print(f"Processing file: {file}")
                # iterating through every article in a file
                for item in data:

                    #if we already have processed that article, we skip it and move to the next article
                    if not check_url.process_url(item["url"], self.urls):
                        continue
                    #adding all words in title to the index
                    if "title" in item:
                        with self.lock:
                            #assigning a new doc_id for the new item, one greater than the last one in the index
                            doc_id = self.global_doc_id[0]
                            self.global_doc_id[0] += 1

                            #creating new sub dictionary for every article
                            self.forward_index[doc_id] = {
                            "w": defaultdict(lambda: {"f": 0, "p": {}})
                        }
                            self.meta_data[doc_id] = {
                                "t": item["title"],
                                "u": item["url"],
                                "a": item["author"],
                                "s": item["source"]
                            }


                        title = item["title"]
                        tokens = word_tokenize(title.lower())
                        x = 1
                        #positions start from 1 for every document
                        self.add(doc_id, tokens, "t", x)

                    #adding all words in content section to the index
                    if "content" in item:
                        content = item["content"]

                        #the position of the next words in the article after title start at a position after title
                        x += len(tokens)
                        tokens = word_tokenize(content.lower())
                        self.add(doc_id, tokens, "c", x)

                    if "author" in item:
                        content = item["author"]

                        x += len(tokens)
                        tokens = word_tokenize(content.lower())
                        self.add(doc_id, tokens, "a", x)
                    if "source" in item:
                        content = item["source"]

                        x += len(tokens)
                        tokens = word_tokenize(content.lower())
                        self.add(doc_id, tokens, "s", x)




            with self.lock:
                self.progress_counter[0] += 1
                print(f"{self.name}: Processed {file}. Progress: {self.progress_counter[0]}/{len(json_files)} files.")


def get_latest_existing_barrel():
    barrel_id = 1
    while os.path.exists(f"forward_index/forward_index_barrel_{barrel_id}.json"):
        barrel_id += 1
    return barrel_id - 1

def build_forward_index(json_files):
    #loads the forward index
    barrel = get_latest_existing_barrel()
    forward_index = load_file(f"forward_index/forward_index_barrel_{barrel}.json")
    meta_data = load_file(f"metadata/metadata_barrel_{barrel}.json")
    #retrives our lexicon
    words = load_file('lexicon.json')
    #retrieve urls that are already in our system
    urls = load_file('urls.json')
    #we declare a global document id with a value one greater than the document id of the last article in the forward index
    if not forward_index:
        last_doc = 0
    else:
        last_doc = list(forward_index.keys())[-1]
    global_doc_id = [int(last_doc) + 1]  # Global counter for unique
    lock = threading.Lock()
    threads = []
    progress_counter = [0]

    chunk_size = 1
    for i in range(0, len(json_files), chunk_size):
        thread = IndexBuilder(json_files[i:i + chunk_size], forward_index, lock, progress_counter, words, urls, global_doc_id, meta_data)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    #returning variables for use outside of function
    return forward_index, words, urls, meta_data


#function for saving data to json files
def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

def divide_into_barrels(articles, num_articles_per_barrel):
    barrels = []
    current_barrel = {}
    counter = 0

    for doc_id, doc_data in articles.items():
        current_barrel[doc_id] = doc_data
        counter += 1

        if counter == num_articles_per_barrel:
            barrels.append(current_barrel)
            current_barrel = {}
            counter = 0

    if current_barrel:
        barrels.append(current_barrel)

    return barrels


def save_barrels(barrels, base_filename, curr):
    for i, barrel in enumerate(barrels):
        filename = f"{base_filename}_{i+curr}.json"
        save_to_json(barrel, filename)


# saving all data to json files
forward_index, words, urls, meta_data = build_forward_index(json_files)

save_to_json(words, 'lexicon.json')
save_to_json(urls, 'urls.json')

# Divide the forward index into barrels of 1000 articles each
num_articles_per_barrel = 1000
barrels = divide_into_barrels(forward_index, num_articles_per_barrel)
meta_data_barrels = divide_into_barrels(meta_data, num_articles_per_barrel)
# Save each barrel
curr = get_latest_existing_barrel()
x = curr
save_barrels(barrels, 'forward_index/forward_index_barrel', curr)
save_barrels(meta_data_barrels, 'metadata/metadata_barrel', x)