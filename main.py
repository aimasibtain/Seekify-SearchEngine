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

json_files = get_json_file_paths(r'D:\Downloads\test2')
#checks if file have been successfully retrieved
print(json_files)

# Mechanism for stop words
import nltk

#run only once. Remove after first execution
nltk.download('punkt')
nltk.download('stopwords')


class IndexBuilder(threading.Thread):
    def __init__(self, file_list, forward_index, lock, progress_counter, words, urls, global_doc_id):
        threading.Thread.__init__(self)
        #initializing the object with the passed values
        self.file_list = file_list
        self.forward_index = forward_index
        self.lock = lock
        self.progress_counter = progress_counter
        self.words = words
        self.urls = urls
        self.global_doc_id = global_doc_id
    #adds words and their respective frequencies and the position and type of each occurrence for a document section
    def add(self, doc_id, tokens, type, count):
        with self.lock:
            #finds the position of each word in the section
            for position, token in enumerate(tokens):
                #filters out stopwords
                if token not in stopwords.words('english'):
                    #checks to see if word is in our lexicon
                    if token not in self.words:
                        #if the word is not present, it is assigned an id and added to the lexicon
                        word_id = len(self.words) + 1
                        self.words[token] = word_id
                    else:
                        # if the word is found, we retrieve its id
                        word_id = self.words[token]
                    #if a list doesn't exist for the type we initialize it
                    if type not in self.forward_index:
                        self.forward_index[doc_id]["words"][word_id]["positions"][type] = []
                    #updating the forward index
                    self.forward_index[doc_id]["words"][word_id]["frequency"] += 1
                    #count is the position from which the section of the article begins
                    self.forward_index[doc_id]["words"][word_id]["positions"][type].append(position+count)
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
                            "title": item["title"],
                            "url": item["url"],
                            "words": defaultdict(lambda: {"frequency": 0, "positions": {}})
                        }

                        title = item["title"]
                        tokens = word_tokenize(title.lower())

                        #positions start from 1 for every document
                        self.add(doc_id, tokens, "t", 1)

                    #adding all words in content section to the index
                    if "content" in item:
                        content = item["content"]

                        #the position of the next words in the article after title dtart at a position after title
                        x = len(tokens) + 1
                        tokens = word_tokenize(content.lower())
                        self.add(doc_id, tokens, "c", x)




            with self.lock:
                self.progress_counter[0] += 1
                print(f"{self.name}: Processed {file}. Progress: {self.progress_counter[0]}/{len(json_files)} files.")


def build_forward_index(json_files):
    #loads the forward index
    forward_index = load_file('forward_index.json')
    #retrives our lexicon
    words = load_file('lexicon.json')
    #retrieve urls that are already in our system
    urls = load_file('urls.json')
    #we declare a global document id with a value one greater than the document id of the last article in the forward index
    global_doc_id = [len(forward_index) + 1]  # Global counter for unique doc_id
    lock = threading.Lock()
    threads = []
    progress_counter = [0]

    chunk_size = 1
    for i in range(0, len(json_files), chunk_size):
        thread = IndexBuilder(json_files[i:i + chunk_size], forward_index, lock, progress_counter, words, urls, global_doc_id)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    #returning variables for use outside of function
    return forward_index, words, urls

#function for saving data to json files
def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# saving all data to json files
forward_index, words, urls = build_forward_index(json_files)
save_to_json(forward_index, 'forward_index.json')
save_to_json(words, 'lexicon.json')
save_to_json(urls, 'urls.json')