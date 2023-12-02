
import os
import json
def get_json_file_paths(root_dir):
    json_file_paths = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                json_file_paths.append(os.path.join(root, file))
    return json_file_paths

def load_file(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as urls:
            return json.load(urls)
    else:
        return {}