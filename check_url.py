import json
import os
def process_url(url, encodings):

    if url not in encodings:
        encodings.append(url)
        return True
    else:
        return False


