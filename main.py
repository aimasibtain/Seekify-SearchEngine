import json
import threading
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

from file_retriever import get_json_file_paths

json_files = get_json_file_paths(r'E:\json\nela-gt-2021\newsdata')
print(json_files) # check to see if all the files have been loaded properly with no path issues


# mechanism for stop words
import nltk
nltk.download('punkt')
nltk.download('stopwords')

class IndexBuilder(threading.Thread):
    def __init__(self, file_list, forward_index, lock, progress_counter):
        threading.Thread.__init__(self)
        self.file_list = file_list
        self.forward_index = forward_index
        self.lock = lock
        self.progress_counter = progress_counter

    def run(self):
        for file in self.file_list:
            with open(file, 'r') as f:
                data = json.load(f)

                if 'content' in data:
                    content = data['content']

                    # tokenization of each word to smoothen the process
                    tokens = word_tokenize(content.lower())
                    unique_tokens = set(tokens)

                    with self.lock:
                        for token in unique_tokens:
                            if token not in stopwords.words('english'):
                                if token not in self.forward_index:
                                    self.forward_index[token] = [file]
                                else:
                                    self.forward_index[token].append(file)

            with self.lock:
                self.progress_counter[0] += 1
                print(f"{self.name}: Processed {file}. Progress: {self.progress_counter[0]}/{len(json_files)} files.")


def build_forward_index(json_files):
    forward_index = defaultdict(list)
    lock = threading.Lock()
    threads = []

    # to monitor the threading progress
    progress_counter = [0]
    
    # splitting files into chunks
    chunk_size = len(json_files) // 10  # initially 10 chunk size has been decided.
    for i in range(0, len(json_files), chunk_size):
        thread = IndexBuilder(json_files[i:i + chunk_size], forward_index, lock, progress_counter)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return forward_index

def save_index_to_json(forward_index, filename):
    with open(filename, 'w') as file:
        json.dump(forward_index, file, indent=4)

# main execution
forward_index = build_forward_index(json_files)
save_index_to_json(forward_index, 'forward_index.json')