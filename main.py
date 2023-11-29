import json
import threading
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

from file_retriever import get_json_file_paths


# Stop words, will keep commented for now
# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')

class IndexBuilder(threading.Thread):
    def __init__(self, file_list, forward_index, lock):
        threading.Thread.__init__(self)
        self.file_list = file_list
        self.forward_index = forward_index
        self.lock = lock

    def run(self):
        for file in self.file_list:
            with open(file, 'r') as f:
                data = json.load(f)
                content = data["content"]

                # tokenization of each word
                tokens = word_tokenize(content.lower())
                unique_tokens = set(tokens)

                with self.lock:
                    for token in unique_tokens:
                        if token not in stopwords.words('english'):
                            if token not in self.forward_index:
                                self.forward_index[token] = [file]
                            else:
                                self.forward_index[token].append(file)

def build_forward_index(json_files):
    forward_index = defaultdict(list)
    lock = threading.Lock()
    threads = []
    
    # Splitting files into chunks
    chunk_size = len(json_files) // 10  # initially 10 chunk size has been decided.
    for i in range(0, len(json_files), chunk_size):
        thread = IndexBuilder(json_files[i:i + chunk_size], forward_index, lock)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return forward_index


json_files = get_json_file_paths("json/nela-gt-2021/newsdata")
forward_index = build_forward_index(json_files)
